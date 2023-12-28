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
    def quantity(self, record):
        """Mapping for Quantity"""
        line_items = []
        total_amount = 0
        divided_tax = 0
        for move in record.move_ids:
            for order_line in record.sale_id.order_line:
                if order_line.product_id != move.product_id:
                    continue
                if order_line.woo_bind_ids.product_uom_qty != move.quantity_done:
                    divided_tax = (
                        float(order_line.woo_bind_ids.total_tax_line)
                        / move.quantity_done
                    )

                    list_item = {
                        "id": order_line.woo_bind_ids.external_id,
                        "quantity": move.quantity_done,
                        "refund_total": int(order_line.woo_bind_ids.price_unit),
                        "refund_tax": [{"refund_total": divided_tax}],
                    }
                    total_amount = (
                        total_amount
                        + int(order_line.woo_bind_ids.price_unit)
                        + divided_tax
                    )
                else:
                    list_item = {
                        "id": order_line.woo_bind_ids.external_id,
                        "quantity": move.quantity_done,
                        "refund_total": int(order_line.woo_bind_ids.price_unit),
                        "refund_tax": [
                            {"refund_total": order_line.woo_bind_ids.total_tax_line}
                        ],
                    }
                    total_amount = (
                        total_amount
                        + int(order_line.woo_bind_ids.price_unit)
                        + int(order_line.woo_bind_ids.total_tax_line)
                    )
                print(total_amount, "wwowowowpowowpwowpowpwowpowpwowpowp")
                line_items.append(list_item)
        print(line_items, "mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm")
        print(total_amount, "dsdudhwudwhuwhuhwuisdhwudhwudwidhu")
        return {
            "amount": str(total_amount),
            "line_items": line_items,
            "api_refund": False,
        }


class WooStockPickingRefundBatchExporter(Component):
    _name = "woo.stock.picking.refund.batch.exporter"
    _inherit = "woo.exporter"
    _apply_on = ["woo.stock.picking.refund"]
