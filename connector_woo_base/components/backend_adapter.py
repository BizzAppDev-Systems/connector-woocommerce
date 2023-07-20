import json
import logging
import socket
import urllib
from datetime import datetime
from urllib.parse import urljoin

import requests
from requests.auth import HTTPBasicAuth
from simplejson.errors import JSONDecodeError

from odoo.addons.component.core import AbstractComponent
from odoo.addons.connector.exception import (
    InvalidDataError,
    NetworkRetryableError,
    RetryableJobError,
)

_logger = logging.getLogger(__name__)


class WooLocation(object):
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
        location = "{location}/wp-json/wc/{version}/".format(
            location=self._location, version=self.version
        )
        return location


class WooClient(object):
    def __init__(self, location, client_id, client_secret, version, test_mode):
        """
        :param location: Woocommerce location for data
        :type location: :class:`WooLocation`
        """
        self._location = location
        self.client_id = client_id
        self.client_secret = client_secret
        self._version = version
        self._test_mode = test_mode

    def get_data(self, arguments):
        """Data for the woo api"""
        if arguments is not None:
            data = json.dumps(arguments)
            return data
        return None

    def call(self, resource_path, arguments, http_method=None, headers=None):
        """send/get request/response to/from remote system"""
        if resource_path is None:
            _logger.exception("Remote System API called without resource path")
            raise NotImplementedError
        url = urljoin(self._location, resource_path)
        kwargs = {"headers": {"content-type": "application/json"}}
        if http_method == "get":
            kwargs["params"] = arguments
        if http_method == "post":
            kwargs["params"] = {"email": arguments.get("email")}
            kwargs["data"] = self.get_data(arguments)
        auth = HTTPBasicAuth(self.client_id, self.client_secret)
        kwargs["auth"] = auth
        function = getattr(requests, http_method)
        response = function(url, **kwargs)
        status_code = response.status_code
        if status_code == 201:
            return response
        try:
            if status_code == 200:
                return response.json()
        except JSONDecodeError:
            if status_code == 400 or status_code == 401 or status_code == 404:
                # From Woo on invalid data we get a 400 error
                # From Woo on Authentication or permission error we get a 401 error,
                # e.g. incorrect API keys
                # From Woo on record don't exist or are missing we get a 404 error
                # but raise_for_status treats it as a network error (which is retryable)
                raise InvalidDataError(
                    "HTTP Error:\n"
                    "Result:%s\n"
                    "Code: %s\n"
                    "Reason: %s\n"
                    "name: %s\n" % (response, status_code, response._content, __name__)
                ) from None
        except urllib.error.HTTPError as err:
            if err.code == 500:
                # Origin Error
                raise NetworkRetryableError(
                    "HTTP Error:\n"
                    "Code: %s\n"
                    "Reason: %s\n"
                    "Headers: %d\n" % (err.code, err.reason, err.headers)
                ) from err
        response.raise_for_status()
        return response.json()


class WooAPI(object):
    def __init__(self, location):
        """
        :param location: Remote location
        :type location: :class:`GenericLocation`
        """
        self._location = location
        self._api = None

    @property
    def api(self):
        if self._api is None:
            remote_client = WooClient(
                self._location.location,
                self._location.client_id,
                self._location.client_secret,
                self._location.test_mode,
                self._location.version,
            )
            self._api = remote_client
        return self._api

    def api_call(self, resource_path, arguments, http_method=None, headers=None):
        """Adjust available arguments per API"""
        if not self.api:
            return self.api
        return self.api.call(resource_path, arguments, http_method=http_method)

    def __enter__(self):
        # we do nothing, api is lazy
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._api is not None and hasattr(self._api, "__exit__"):
            self._api.__exit__(exc_type, exc_value, traceback)

    def call(self, resource_path, arguments, http_method=None, headers=None):
        try:
            if isinstance(arguments, list):
                while arguments and arguments[-1] is None:
                    arguments.pop()
            start = datetime.now()
            try:
                result = self.api_call(
                    resource_path, arguments, http_method=http_method, headers=headers
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
            # Uncomment to record requests/responses in ``recorder``
            # record(method, arguments, result)
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


class WooCRUDAdapter(AbstractComponent):
    """External Records Adapter for Woocommerce"""

    # pylint: disable=method-required-super

    _name = "woo.crud.adapter"
    _inherit = ["base.backend.adapter", "connector.woo.base"]
    _usage = "backend.adapter"

    def search(self, filters=None):
        """
        Search records according to some criterias
        and returns a list of ids
        """
        raise NotImplementedError

    def read(self, external_id, attributes=None):
        """Returns the information of a record"""
        raise NotImplementedError

    def search_read(self, filters=None):
        """
        Search records according to some criterias
        and returns their information
        """
        raise NotImplementedError

    def create(self, data):
        """Create a record on the external system"""
        raise NotImplementedError

    def write(self, external_id, data):
        """Update records on the external system"""
        raise NotImplementedError

    def delete(self, external_id):
        """Delete a record on the external system"""
        raise NotImplementedError

    def _call(self, resource_path, arguments=None, http_method=None):
        """Method to initiate the connection"""
        try:
            woo_api = getattr(self.work, "woo_api")
        except AttributeError:
            raise AttributeError(
                "You must provide a woo_api attribute with a "
                "WooAPI instance to be able to use the "
                "Backend Adapter."
            ) from None
        return woo_api.call(resource_path, arguments, http_method=http_method)


class GenericAdapter(AbstractComponent):
    # pylint: disable=method-required-super

    _name = "woo.adapter"
    _inherit = "woo.crud.adapter"
    _apply_on = "woo.backend"

    _woo_model = None
    _last_update_field = None
    _woo_ext_id_key = "id"
    _odoo_ext_id_key = "external_id"

    def search_read(self, filters=None, **kwargs):
        """Method to get the records from woo"""
        result = self._call(
            resource_path=self._woo_model, arguments=filters, http_method="get"
        )
        return result

    def read(self, external_id=None, attributes=None):
        """Method to get a data for specified record"""
        result = self._call(resource_path=self._woo_model, http_method="get")
        return result

    def create(self, data):
        """Creates the data in remote"""
        result = self._call(self._woo_model, data, http_method="post")
        return result
