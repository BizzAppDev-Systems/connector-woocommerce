import logging
from odoo import _
from odoo.addons.component.core import Component
from odoo.addons.connector.exception import MappingError
from odoo.addons.connector.components.mapper import mapping

_logger = logging.getLogger(__name__)


class WooSaleOrderExporterMapper(Component):
    _name = "woo.sale.order.export.mapper"
    _inherit = "woo.export.mapper"
    _apply_on = "woo.sale.order"

    @mapping
    def status(self, record):
        """Mapping for Status"""
        return (
            {"status": "completed"}
            if record.picking_ids.state == "done" and self.backend_record.mark_completed
            else {}
        )

    @mapping
    def tracking_number(self, record):
        """Mapping for tracking number"""
        tracking_number = False
        done_pickings = record.picking_ids.filtered(
            lambda picking: picking.state == "done"
        )
        if (
            self.backend_record.tracking_info
            and not done_pickings[0].carrier_tracking_ref
        ):
            raise MappingError(_("Tracking Info not found!"))
        tracking_number = done_pickings[0].carrier_tracking_ref
        return {
            "meta_data": [
                {
                    "key": "_wc_shipment_tracking_items",
                    "value": [
                        {
                            "tracking_number": tracking_number,
                        }
                    ],
                }
            ]
        }


class WooSaleOrderBatchExporter(Component):
    _name = "woo.sale.order.batch.exporter"
    _inherit = "woo.exporter"
    _apply_on = ["woo.sale.order"]

    def _after_export(self, binding):
        """Import the transaction lines after checking WooCommerce order status."""
        binding.write({"woo_order_status": "completed"})
