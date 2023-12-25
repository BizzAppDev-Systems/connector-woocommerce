import json

from odoo import http
from odoo.http import request


class WooWebhook(http.Controller):
    def _common_webhook_handler(self, access_token, model_name):
        """Common handler for processing WooCommerce webhooks."""
        job_options = {}
        payload = json.loads(request.httprequest.data)
        backend = (
            request.env["woo.backend"]
            .sudo()
            .search([("access_token", "=", access_token)], limit=1)
        )
        model = request.env[model_name]
        description = backend.get_queue_job_description(
            prefix=model.import_record.__doc__ or f"Record Import Of {model_name}",
            model=model._description,
        )
        job_options["description"] = description

        return model.with_delay(**job_options or {}).import_record(
            backend=backend, external_id=payload.get("id"), data=payload
        )

    @http.route(
        [
            "/create_product/woo_webhook/<access_token>",
            "/update_product/woo_webhook/<access_token>",
        ],
        methods=["POST"],
        type="json",
        auth="public",
        website=True,
    )
    def handle_product_webhook(self, access_token, **kwargs):
        """Handle WooCommerce product webhooks."""
        return self._common_webhook_handler(access_token, "woo.product.product")

    @http.route(
        [
            "/create_order/woo_webhook/<access_token>",
            "/update_order/woo_webhook/<access_token>",
        ],
        methods=["POST"],
        type="json",
        auth="public",
        website=True,
    )
    def handle_order_webhook(self, access_token, **kwargs):
        """Handle WooCommerce order webhooks."""
        return self._common_webhook_handler(access_token, "woo.sale.order")
