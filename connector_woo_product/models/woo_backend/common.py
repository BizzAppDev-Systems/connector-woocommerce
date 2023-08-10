from datetime import datetime, timedelta

from odoo import fields, models

IMPORT_DELTA_BUFFER = 30  # seconds


class WooBackend(models.Model):
    """Backend for WooCommerce"""

    _inherit = "woo.backend"

    import_products_from_date = fields.Datetime(string="Import products from date")

    def import_products(self):
        """Import Products from backend"""
        for backend in self:
            backend._import_from_date(
                model="woo.product.product",
                from_date_field="import_products_from_date",
                priority=5,
            )
        return True

    def cron_import_products(self, domain=None):
        """Cron for import_products"""
        backend_ids = self.search(domain or [])
        backend_ids.import_products()

    def import_product_attributes(self):
        """Import Products from backend"""
        for backend in self:
            filters = {"per_page": backend.default_limit, "page": 1}
            backend.env["woo.product.attribute"].with_company(
                backend.company_id
            ).with_delay(priority=5).import_batch(backend=backend, filters=filters)

    def cron_import_product_attributes(self, domain=None):
        """Cron for import_product_attributes"""
        backend_ids = self.search(domain or [])
        backend_ids.import_product_attributes()

    def import_product_categories(self):
        """Import Product Category from backend"""
        for backend in self:
            filters = {"per_page": backend.default_limit, "page": 1}
            backend.env["woocommerce.product.category"].with_company(
                backend.company_id
            ).with_delay(priority=5).import_batch(backend=backend, filters=filters)

    def cron_import_product_categories(self, domain=None):
        """Cron for import_product_categories"""
        backend_ids = self.search(domain or [])
        backend_ids.import_product_categories()

    def _import_from_date(self, model, from_date_field, priority=None):
        """Method to add a filter based on the date."""
        import_start_time = datetime.now()
        job_options = {}
        if priority or priority == 0:
            job_options["priority"] = priority
        for backend in self:
            from_date = backend[from_date_field]
            if from_date:
                from_date = fields.Datetime.from_string(from_date)
            else:
                from_date = None
            self.env[model].with_delay(**job_options or {}).import_batch(
                backend,
                {
                    "per_page": backend.default_limit,
                    "page": 1,
                    "after": from_date,
                },
            )
        # Records from Woo are imported based on their `created_at`
        # date.  This date is set on Woo at the beginning of a
        # transaction, so if the import is run between the beginning and
        # the end of a transaction, the import of a record may be
        # missed.  That's why we add a small buffer back in time where
        # the eventually missed records will be retrieved.  This also
        # means that we'll have jobs that import twice the same records,
        # but this is not a big deal because they will be skipped when
        # the last `sync_date` is the same.
        next_time = import_start_time - timedelta(seconds=IMPORT_DELTA_BUFFER)
        next_time = fields.Datetime.to_string(next_time)
        self.write({from_date_field: next_time})
