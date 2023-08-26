from odoo import fields, models


class WooBackend(models.Model):
    """Backend for WooCommerce"""

    _inherit = "woo.backend"

    mark_completed = fields.Boolean(string="Mark Order Completed On Delivery")
    tracking_info = fields.Boolean(string="Send Tracking Information")

    def import_sale_orders(self):
        """Import Orders from backend"""
        filters = {"page": 1}
        for backend in self:
            filters.update({"per_page": backend.default_limit})
            backend.env["woo.sale.order"].with_company(backend.company_id).with_delay(
                priority=10
            ).import_batch(backend=backend, filters=filters)

    def cron_import_sale_orders(self, domain=None):
        """Cron for import_sale_orders"""
        backend_ids = self.search(domain or [])
        backend_ids.import_sale_orders()

    def export_stock_picking_status(self):
        """Export Stock Picking status"""
        for backend in self.sudo():
            backend._export_from_date(
                model="woo.stock.picking",
                priority=20,
            )

    def cron_export_stock_picking_status(self, domain=None):
        """Cron for Export Stock Picking Status"""
        backend_ids = self.search(domain or [])
        backend_ids.export_stock_picking_status()

    def export_sale_order_status(self):
        """Export Sale Order Status"""
        filters = {"page": 1}
        for backend in self:
            filters.update({"per_page": backend.default_limit})
            self.env["woo.sale.order"].with_company(backend.company_id).with_delay(
                priority=15
            ).export_batch(backend=backend, filters=filters)

    def cron_export_sale_order_status(self, domain=None):
        """Cron of Export sale order status"""
        backend_ids = self.search(domain or [])
        backend_ids.export_sale_order_status()
