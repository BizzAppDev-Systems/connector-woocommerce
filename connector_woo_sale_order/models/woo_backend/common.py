from datetime import datetime, timedelta

from odoo import api, fields, models

IMPORT_DELTA_BUFFER = 30


class WooBackend(models.Model):
    """Backend for WooCommerce"""

    _inherit = "woo.backend"

    mark_completed = fields.Boolean(string="Mark Order Completed On Delivery")
    tracking_info = fields.Boolean(string="Send Tracking Information")
    import_orders_from_date = fields.Datetime(string="Import Orders from date")
    order_prefix = fields.Char(string="Sale Order Prefix", default="WOO_")

    def _import_from_date(self, model, from_date_field, priority=None, filters=None):
        """Method to add a filter based on the date."""
        import_start_time = datetime.now()
        job_options = {}
        if priority or priority == 0:
            job_options["priority"] = priority
        from_date = self[from_date_field]
        if from_date:
            filters["after"] = self.import_orders_from_date
            from_date = fields.Datetime.from_string(from_date)
        else:
            from_date = None
        self.env[model].with_delay(**job_options or {}).import_batch(
            backend=self, filters=filters
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

    def import_sale_orders(self):
        """Import Orders from backend"""
        filters = {"page": 1}
        for backend in self:
            filters.update({"per_page": backend.default_limit})
            backend._import_from_date(
                model="woo.sale.order",
                from_date_field="import_orders_from_date",
                priority=5,
                filters=filters,
            )
        return True

    @api.model
    def cron_import_sale_orders(self, domain=None):
        """Cron for import_sale_orders"""
        backend_ids = self.search(domain or [])
        backend_ids.import_sale_orders()

    def export_sale_order_status(self):
        """Export Sale Order Status"""
        filters = {"page": 1}
        for backend in self:
            filters.update({"per_page": backend.default_limit})
            self.env["woo.sale.order"].with_delay(priority=15).export_batch(
                backend=backend, filters=filters
            )

    @api.model
    def cron_export_sale_order_status(self, domain=None):
        """Cron of Export sale order status"""
        backend_ids = self.search(domain or [])
        backend_ids.export_sale_order_status()
