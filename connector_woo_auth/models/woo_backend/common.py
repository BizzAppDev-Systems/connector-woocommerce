import logging
import requests
from odoo import fields, models, _
from requests_oauthlib import OAuth1Session
from odoo.exceptions import ValidationError
import random
import string
import time

current_timestamp = int(time.time())
_logger = logging.getLogger(__name__)

IMPORT_DELTA_BUFFER = 30  # seconds


class WooBackend(models.Model):
    """Backend for WooCommerce"""

    _inherit = ["woo.backend"]

    authentication_type = fields.Selection(
        selection=[("api_key", "API Key"), ("auth_1.0", "OAuth 1.0")],
        default="api_key",
    )
    test_callback_url = fields.Char()

    def request_token(self):
        """Step 1: Get a request token. This is a temporary token that is used for
        having the user authorize an access token and to sign the request to obtain"""

        # REQUEST_TOKEN_URL = "https://trello.com/1/OAuthGetRequestToken"
        # AUTHORIZE_URL = "https://trello.com/1/OAuthAuthorizeToken"
        # callback_url = "{}?backend_id={}".format(self.test_callback_url, self.id)
        # oauth_timestamp = current_timestamp
        # oauth_nonce = self.generate_nonce()
        # oauth_signature_method = "HMAC-SHA1"

        # if self.test_mode:
        #     oauth_consumer_key = self.test_client_id

        # else:
        #     oauth_consumer_key = self.client_id

        # oauth_signature
        # session = OAuth1Session(
        #     client_key=key, client_secret=secret, callback_uri=callback_url
        # )
        # response = session.fetch_request_token(url=REQUEST_TOKEN_URL)
        # resourceOwnerKey, resourceOwnerSecret = response.get(
        #     "oauth_token"
        # ), response.get("oauth_token_secret")

        # self.oauth_token = resourceOwnerKey
        # self.oauth_token_secret = resourceOwnerSecret
        # url = (
        #     "{authorize_url}?oauth_token={oauth_token}&scope={scope}"
        #     "&expiration={expiration}&name={name}".format(
        #         authorize_url=AUTHORIZE_URL,
        #         oauth_token=resourceOwnerKey,
        #         expiration="30days",
        #         scope=scope,
        #         name=name,
        #     )
        # )
        # response = requests.get(url, timeout=10)

        # if response.status_code == 200:
        #     # URL response is successful (HTTP 200)
        #     return {
        #         "type": "ir.actions.act_url",
        #         "url": url,
        #     }
        # else:
        #     # URL response is not successful
        #     raise ValidationError(_("Please Enter Valid Credentials......"))

    def generate_nonce(length=32):
        # Generate a random string of 'length' characters
        nonce_characters = string.ascii_letters + string.digits
        return "".join(random.choice(nonce_characters) for _ in range(length))
