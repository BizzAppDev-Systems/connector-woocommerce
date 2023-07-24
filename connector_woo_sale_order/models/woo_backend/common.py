from odoo import models

IMPORT_DELTA_BUFFER = 30  # seconds


class WooBackend(models.Model):
    """Backend for WooCommerce"""

    _inherit = "woo.backend"

    def import_sale_orders(self):
        """Import Orders from backend"""
        for backend in self:
            filters = {"per_page": backend.default_limit, "page": 1}
            backend.env["woo.sale.order"].with_company(
                backend.company_id
            ).with_delay(priority=5).import_batch(backend=backend, filters=filters)

    def cron_import_sale_orders(self, domain=None):
        """Cron for import_sale_orders"""
        backend_ids = self.search(domain or [])
        backend_ids.import_sale_orders()
