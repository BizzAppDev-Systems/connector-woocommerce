from odoo import models
from odoo import fields, models

IMPORT_DELTA_BUFFER = 30  # seconds


class WooBackend(models.Model):
    """Backend for WooCommerce"""

    _inherit = "woo.backend"

    mark_completed = fields.Boolean(string="Mark Order Completed On Delivery")
    tracking_info = fields.Boolean(string="Send Tracking Information")

    def import_sale_orders(self):
        """Import Orders from backend"""
        for backend in self:
            filters = {"per_page": backend.default_limit, "page": 1}
            backend.env["woo.sale.order"].with_company(backend.company_id).with_delay(
                priority=5
            ).import_batch(backend=backend, filters=filters)

    def cron_import_sale_orders(self, domain=None):
        """Cron for import_sale_orders"""
        backend_ids = self.search(domain or [])
        backend_ids.import_sale_orders()

    # Export Stock Picking status
    def export_stock_picking_status(self):
        for backend in self.sudo():
            backend._export_from_date(
                model="woo.stock.picking",
                priority=20,
            )

    def cron_export_stock_picking_status(self, domain=None):
        backend_ids = self.search(domain or [])
        backend_ids.export_stock_picking_status()

    def export_sale_order_status(self):
        for backend in self:
            filters = {"per_page": backend.default_limit, "page": 1}
            self.env["woo.sale.order"].with_company(backend.company_id).with_delay(
                priority=5
            ).export_batch(backend=backend, filters=filters)

    def cron_export_sale_order_status(self, domain=None):
        backend_ids = self.search(domain or [])
        backend_ids.export_sale_order_status()
