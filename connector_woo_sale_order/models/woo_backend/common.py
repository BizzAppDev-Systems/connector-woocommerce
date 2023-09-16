from odoo import api, fields, models

IMPORT_DELTA_BUFFER = 30


class WooBackend(models.Model):
    """Backend for WooCommerce"""

    _inherit = "woo.backend"

    mark_completed = fields.Boolean(
        string="Mark Order Completed On Delivery",
        help="""If Mark Completed is True,
        we can update the sale order status export functionality
        for WooCommerce orders whose status is not completed.""",
    )
    tracking_info = fields.Boolean(
        string="Send Tracking Information",
        help="""If Mark Completed is True, this field will be visible,
        and we can add tracking information at the DO (Delivery Order) level to
        update the sale order status as well as Tracking Info in WooCommerce.""",
    )
    import_orders_from_date = fields.Datetime(string="Import Orders from date")
    order_prefix = fields.Char(string="Sale Order Prefix", default="WOO_")

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
            sale_orders = self.env["sale.order"].search(
                [("woo_bind_ids.backend_id", "=", backend.id)]
            )
            for sale_order in sale_orders:
                sale_order.with_delay(priority=5).export_delivery_status()

    @api.model
    def cron_export_sale_order_status(self, domain=None):
        """Cron of Export sale order status"""
        backend_ids = self.search(domain or [])
        backend_ids.export_sale_order_status()
