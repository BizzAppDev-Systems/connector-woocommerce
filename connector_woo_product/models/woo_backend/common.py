from odoo import models

IMPORT_DELTA_BUFFER = 30  # seconds


class WooBackend(models.Model):
    """Backend for WooCommerce"""

    _inherit = "woo.backend"

    def import_products(self):
        """Import Partners from backend"""
        for backend in self:
            filters = {}
            filters["per_page"] = backend.default_limit
            filters["page"] = 1
            backend.env["woo.product.product"].with_company(
                backend.company_id
            ).with_delay(priority=5).import_batch(backend=backend, filters=filters)

    def cron_import_products(self, domain=None):
        """Cron for import_products"""
        backend_ids = self.search(domain or [])
        backend_ids.import_products()
