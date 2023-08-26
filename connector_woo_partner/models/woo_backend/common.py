from odoo import models


class WooBackend(models.Model):
    """Backend for WooCommerce"""

    _inherit = "woo.backend"

    def import_partners(self):
        """Import Partners from backend"""
        filters = {"page": 1}
        for backend in self:
            filters.update({"per_page": backend.default_limit})
            backend.env["woo.res.partner"].with_company(backend.company_id).with_delay(
                priority=5
            ).import_batch(backend=backend, filters=filters)

    def cron_import_partners(self, domain=None):
        backend_ids = self.search(domain or [])
        backend_ids.import_partners()
