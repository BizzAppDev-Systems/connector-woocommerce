from odoo import api, fields, models


class WooBackend(models.Model):
    """Backend for WooCommerce"""

    _inherit = "woo.backend"

    import_partners_from_date = fields.Datetime(string="Import partners from date")
    without_email = fields.Boolean(string="Allow Partners without Email")

    def import_partners(self):
        """Import Partners from backend"""
        filters = {"page": 1}
        for backend in self:
            filters.update({"per_page": backend.default_limit})
            backend.env["woo.res.partner"].with_delay(priority=5).import_batch(
                backend=backend, filters=filters
            )

    @api.model
    def cron_import_partners(self, domain=None):
        backend_ids = self.search(domain or [])
        backend_ids.import_partners()
