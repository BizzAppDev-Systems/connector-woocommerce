import logging

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping

# from odoo.exceptions import ValidationError


_logger = logging.getLogger(__name__)


class WooStockPickingRefundExporterMapper(Component):
    _name = "woo.stock.picking.refund.export.mapper"
    _inherit = "woo.export.mapper"
    _apply_on = "woo.stock.picking.refund"

    @mapping
    def status(self, record):
        """Mapping for Status"""
        print(record, "ssssssssssssssssssssssssssssssssssss")
        line_items = [{"id": "349","quantity": line["product_qty"],"refund_total": 18}]
        for product in record:


        return {
            "amount": "18",
            "line_items": line_items,
            "api_refund": False,
        }

    #     if record.is_final_status:
    #         raise MappingError(
    #             _("WooCommerce Sale Order is already in Completed Status.")
    #         )
    #     if not self.backend_record.mark_completed:
    #         raise MappingError(
    #             _(
    #                 "Export Delivery Status is Not Allow from WooCommerce"
    #                 " Backend '%s'.",
    #                 self.backend_record.name,
    #             )
    #         )
    #     return {"status": "completed"}

    # @mapping
    # def tracking_number(self, record):
    #     """Mapping for tracking number"""
    #     tracking_number = False
    #     if not self.backend_record.tracking_info:
    #         return {}
    #     done_pickings = record.picking_ids.filtered(
    #         lambda picking: picking.state == "done"
    #     )
    #     if not done_pickings:
    #         raise MappingError(_("No delivery orders in 'done' state."))
    #     if (
    #         self.backend_record.tracking_info
    #         and not done_pickings[0].carrier_tracking_ref
    #     ):
    #         raise MappingError(
    #             _("Tracking Reference not found in Delivery Order! %s")
    #             % done_pickings[0].name
    #         )
    #     tracking_number = done_pickings[0].carrier_tracking_ref
    #     return {
    #         "meta_data": [
    #             {
    #                 "key": "_wc_shipment_tracking_items",
    #                 "value": [
    #                     {
    #                         "tracking_number": tracking_number,
    #                     }
    #                 ],
    #             }
    #         ]
    #     }


class WooStockPickingRefundBatchExporter(Component):
    _name = "woo.stock.picking.refund.batch.exporter"
    _inherit = "woo.exporter"
    _apply_on = ["woo.stock.picking.refund"]

    # def _after_export(self, binding):
    #     """Import the transaction lines after checking WooCommerce order status."""
    #     woo_order_status = self.env["woo.sale.status"].search(
    #         [("code", "=", "completed"), ("is_final_status", "=", True)], limit=1
    #     )
    #     if not woo_order_status:
    #         raise ValidationError(
    #             _(
    #                 "The WooCommerce order status with the code 'completed' is not "
    #                 "available in Odoo or isn't marked as 'Final Status'."
    #             )
    #         )
    #     binding.write({"woo_order_status_id": woo_order_status.id})
    #     binding.write({"woo_order_status": "completed"})
