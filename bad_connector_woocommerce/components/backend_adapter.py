import logging
import socket
import urllib
from datetime import datetime

import requests
from woocommerce import API

from odoo.addons.connector.exception import NetworkRetryableError, RetryableJobError
from odoo.addons.connector_base.components.backend_adapter import (
    GenericAdapter,
    GenericAPI,
)

_logger = logging.getLogger(__name__)


class WooLocation:
    """The Class is used to set Location"""

    def __init__(self, location, client_id, client_secret, version, test_mode):
        """Initialization to set location"""
        self._location = location
        self.client_id = client_id
        self.client_secret = client_secret
        self.version = version
        self.test_mode = test_mode

    @property
    def location(self):
        return self._location


class WooAPI(GenericAPI):
    def __init__(self, location):
        """
        :param location: Remote location
        :type location: :class:`GenericLocation`
        """
        self._location = location.get("location")
        self._api = None

    @property
    def api(self):
        if self._api is None:
            woocommerce_client = API(
                url=self._location.location,
                consumer_key=self._location.client_id,
                consumer_secret=self._location.client_secret,
                version=self._location.version,
                wp_api=True,
            )
            self._api = woocommerce_client
        return self._api

    def api_call(self, resource_path, arguments, http_method=None):
        """Adjust available arguments per API"""
        if not self.api:
            return self.api
        http_method = http_method.lower()
        additional_data = {}
        if http_method == "get":
            additional_data.update(params=arguments)
        else:
            additional_data.update(data=arguments)
        return getattr(self.api, http_method)(resource_path, **additional_data)

    def call(
        self, resource_path, arguments, http_method=None, is_token=False, **kwargs
    ):
        try:
            if isinstance(arguments, list):
                while arguments and arguments[-1] is None:
                    arguments.pop()
            start = datetime.now()
            try:
                result = self.api_call(
                    resource_path, arguments, http_method=http_method
                )
            except Exception:
                _logger.error("api.call('%s', %s) failed", resource_path, arguments)
                raise
            else:
                _logger.debug(
                    "api.call('%s', %s) returned %s in %s seconds",
                    resource_path,
                    arguments,
                    result,
                    (datetime.now() - start).seconds,
                )
            status_code = result.status_code
            if status_code == 201:
                return result
            if status_code == 200:
                json_response = result.json()
                record_count = result.headers.get("X-WP-Total")
                return {"record_count": record_count, "data": json_response}
            if (
                status_code == 400
                or status_code == 401
                or status_code == 404
                or status_code == 500
            ):
                # From Woo on invalid data we get a 400 error
                # From Woo on Authentication or permission error we get a 401 error,
                # e.g. incorrect API keys
                # From Woo on record don't exist or are missing we get a 404 error
                # but raise_for_status treats it as a network error (which is retryable)
                raise requests.HTTPError(
                    self._location.location,
                    result.status_code,
                    result._content,
                    __name__,
                )
            result.raise_for_status()
            return result
        except (socket.gaierror, socket.error, socket.timeout) as err:
            raise NetworkRetryableError(
                "A network error caused the failure of the job: " "%s" % err
            ) from err
        except urllib.error.HTTPError as err:
            if err.code in [502, 503, 504]:
                # Origin Error
                raise RetryableJobError(
                    "HTTP Error:\n"
                    "Code: %s\n"
                    "Reason: %s\n"
                    "Headers: %d\n" % (err.code, err.reason, err.headers)
                ) from err
            else:
                raise


class WooAdapter(GenericAdapter):
    # pylint: disable=method-required-super

    _name = "woo.adapter"
    _inherit = "generic.adapter"
    _remote_model = None
    _last_update_date = "date_modified"
    _remote_datetime_format = "%Y-%m-%dT%H:%M:%S"
    _woo_product_stock = None
    _woo_default_currency = None
    _woo_default_weight = None
    _woo_default_dimension = None

    def search(self, filters=None, http_method=None, **kwargs):
        """
        Inherited Method to get the records of settings from WooCommerce
        """
        resource_path = self.get_default_resource_path(
            "search", filters=filters, **kwargs
        )
        http_method = http_method or self._http_method
        result = self._call(
            resource_path, arguments=filters, http_method="get", **kwargs
        )
        if kwargs.get("_woo_product_stock", False):
            setting_stock_result = self._call(
                resource_path=kwargs.get("_woo_product_stock"),
                arguments=filters,
                http_method="get",
                **kwargs,
            )
            result["data"].append(setting_stock_result.get("data"))

        if kwargs.get("_woo_default_currency", False):
            default_currency_result = self._call(
                resource_path=kwargs.get("_woo_default_currency"),
                arguments=filters,
                http_method="get",
            )
            result["data"].append(default_currency_result.get("data"))

        if kwargs.get("_woo_default_weight", False):
            default_weight_result = self._call(
                resource_path=kwargs.get("_woo_default_weight"),
                arguments=filters,
                http_method="get",
            )
            result["data"].append(default_weight_result.get("data"))

        if kwargs.get("_woo_default_dimension", False):
            default_dimension_result = self._call(
                resource_path=kwargs.get("_woo_default_dimension"),
                arguments=filters,
                http_method="get",
            )
            result["data"].append(default_dimension_result.get("data"))

        return result
