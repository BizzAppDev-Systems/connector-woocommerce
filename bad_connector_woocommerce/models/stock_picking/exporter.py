import logging

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from odoo.addons.connector.exception import MappingError

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
        total_amount = 0.00
        divided_tax = 0
        sale_order_products = {
            order_line.product_id.id for order_line in record.sale_id.order_line
        }
        for move in record.move_ids:
            if move.product_id.id in sale_order_products:
                order_line = next(
                    order_line
                    for order_line in record.sale_id.order_line
                    if order_line.product_id.id == move.product_id.id
                )
                if move.quantity_done > order_line.woo_bind_ids[0].product_uom_qty:
                    raise MappingError(
                        _(
                            "Quantity done of move line is greater than quantity in WooCommerce Product Quantity."
                        )
                    )

                if order_line.woo_bind_ids.product_uom_qty > move.quantity_done:
                    print(
                        order_line.woo_bind_ids[0].total_tax_line,
                        "totallll taxxxx line",
                    )
                    print(move.quantity_done, "quuuaannntityyyyy doneeee")
                    divided_tax = (
                        float(order_line.woo_bind_ids[0].total_tax_line)
                        / order_line.woo_bind_ids[0].product_uom_qty
                    )
                    print(divided_tax, "dwowookokokokokokokokokokokokoko")

                    list_item = {
                        "id": order_line.woo_bind_ids[0].external_id,
                        "quantity": move.quantity_done,
                        "refund_total": float(order_line.woo_bind_ids[0].price_unit),
                        "refund_tax": [
                            {
                                "id": str(record.sale_id.id),
                                "refund_total": divided_tax,
                            }
                        ],
                    }
                    total_amount = (
                        total_amount
                        + float(order_line.woo_bind_ids[0].price_unit) * divided_tax
                    )
                else:
                    list_item = {
                        "id": order_line.woo_bind_ids[0].external_id,
                        "quantity": move.quantity_done,
                        "refund_total": float(order_line.woo_bind_ids[0].price_unit),
                        "refund_tax": [
                            {
                                "id": str(record.sale_id.id + 1),
                                "refund_total": float(
                                    order_line.woo_bind_ids[0].total_tax_line
                                ),
                            }
                        ],
                    }
                    print(list_item, "jddiijisjiwsjwisjwisjiwsjwisjisji")
                    total_amount = (
                        total_amount
                        + float(order_line.woo_bind_ids[0].price_unit)
                        + float(order_line.woo_bind_ids[0].total_tax_line)
                    )
                line_items.append(list_item)
        print(line_items, "mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm")
        print(total_amount, "dsdudhwudwhuwhuhwuisdhwudhwudwidhu")
        return {
            "order_id": record.sale_id.woo_bind_ids[0].external_id,
            "amount": str(total_amount),
            "line_items": line_items,
            "api_refund": False,
        }


class WooStockPickingRefundBatchExporter(Component):
    _name = "woo.stock.picking.refund.batch.exporter"
    _inherit = "woo.exporter"
    _apply_on = ["woo.stock.picking.refund"]
