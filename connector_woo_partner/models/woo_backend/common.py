from odoo import fields, models

from odoo.addons.connector_woo_base.components.misc import get_queue_job_description


class WooBackend(models.Model):
    """Backend for WooCommerce"""

    _inherit = "woo.backend"
    import_partners_from_date = fields.Datetime(string="Import partners from date")
    without_email = fields.Boolean(string="Allow Partners without Email")

    def import_partners(self):
        """Import Partners from backend"""
        filters = {"page": 1}
        job_options = {}
        for backend in self:
            filters.update({"per_page": backend.default_limit})
            job_options["description"] = get_queue_job_description(
                model_name="woo.res.partner", batch=True, job_type="Import"
            )
            backend.env["woo.res.partner"].with_company(backend.company_id).with_delay(
                priority=5
            ).import_batch(backend=backend, filters=filters)

    def cron_import_partners(self, domain=None):
        backend_ids = self.search(domain or [])
        backend_ids.import_partners()
