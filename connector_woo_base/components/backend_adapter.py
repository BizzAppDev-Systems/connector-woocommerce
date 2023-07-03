import logging
from urllib.parse import urljoin
from datetime import datetime
from odoo.addons.queue_job.exception import RetryableJobError
import socket
from odoo.addons.component.core import AbstractComponent
import urllib
from odoo.addons.connector.exception import NetworkRetryableError, InvalidDataError
import requests
import json
from requests.auth import HTTPBasicAuth
from simplejson.errors import JSONDecodeError

_logger = logging.getLogger(__name__)


class WooAPI(object):
    def __init__(self, location, client_id, client_secret, version):
        self.location = location
        self.client_id = client_id
        self.client_secret = client_secret
        self.version = version

    def __enter__(self):
        """We do nothing, api is lazy"""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Trace-back of API"""
        pass

    def api_call(self, resource_path, arguments, http_method=None):
        """Do requests"""
        url = urljoin(self.location, resource_path.format(version=self.version))
        auth = None
        headers = {}
        params = {}
        data = {}
        if self.client_id and self.client_secret:
            if http_method == "post":
                params["email"] = arguments.get("email")
                data = json.dumps(arguments)
            auth = HTTPBasicAuth(self.client_id, self.client_secret)
        response = requests.request(
            method=http_method,
            url=url,
            auth=auth,
            data=data,
            headers=headers,
            params=params,
            timeout=5,
        )
        return response

    def call(self, resource_path, arguments, http_method=None):
        """send/get request/response to/from remote system"""
        result = self.api_call(
            resource_path=resource_path,
            arguments=arguments,
            http_method=http_method,
        )
        status_code = result.status_code
        json_data = result.json()

        if status_code == 201:
            return result
        elif status_code == 200:
            return json_data
        elif status_code == 400 or status_code == 401 or status_code == 404:
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
                "name: %s\n" % (result, status_code, result._content, __name__)
            )
        elif status_code == 500:
            # In case Server Error/Network Error
            raise NetworkRetryableError(
                "HTTP Error:\n"
                "Result:%s\n"
                "Code: %s\n"
                "Reason: %s\n"
                "name: %s\n" % (result, status_code, result._content, __name__)
            )
        result.raise_for_status()


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
            )
        return woo_api.call(resource_path, arguments, http_method=http_method)


class GenericAdapter(AbstractComponent):
    # pylint: disable=method-required-super

    _name = "woo.adapter"
    _inherit = "woo.crud.adapter"

    _woo_model = None
    _woo_ext_id_key = None
    _odoo_ext_id_key = None
    _woo_fallback_ext_id_kay = None
    _woo_model_type = "/wp-json/"
    _last_update_field = None
    _apply_on = "woo.backend"

    def search_read(self, filters=None, **kwargs):
        """Method to get the records from woo"""
        resource_path = urljoin(self._woo_model_type, self._woo_model)
        result = self._call(
            resource_path=resource_path, arguments=filters, http_method="get"
        )
        return result

    def read(self, external_id=None, attributes=None):
        """Method to get a data for specified record"""
        resource_path = urljoin(self._woo_model_type, self._woo_model)
        resource_path = "{}/{}".format(resource_path, external_id)
        result = self._call(resource_path=resource_path, http_method="get")
        return result

    def create(self, data):
        """Creates the data in remote"""
        resource_path = urljoin(self._woo_model_type, self._woo_model)
        result = self._call(resource_path, data, http_method="post")
        return result

    def write(self, external_id, data):
        """Update the data in remote"""
        pass

    # TODO : Support method as needed

    def search(self, filters=None):
        pass

    def delete(self, external_id):
        pass

    def cancel(self, external_id):
        pass

    def complete(self, external_id):
        pass
