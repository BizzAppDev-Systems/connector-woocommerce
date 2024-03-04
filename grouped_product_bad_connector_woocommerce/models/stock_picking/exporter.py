import logging

from odoo import _
from odoo.tools import html2plaintext

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from odoo.addons.connector.exception import MappingError

_logger = logging.getLogger(__name__)


class WooStockPickingRefundExporterMapper(Component):
    _inherit = "woo.stock.picking.refund.export.mapper"

    @mapping
    def quantity_and_amount(self, record):
        """Mapping for Quantity and Amount"""
        line_items = []
        total_amount = 0.00
        sale_order_products = {
            order_line.product_id for order_line in record.sale_id.order_line
        }
        print(sale_order_products, "llllllllllllllllll sale_order_products")
        for move in record.move_ids:
            # if move.product_id.id not in sale_order_products:
            #     continue
            print(move.picking_id.sale_id.order_line[0].product_id, "ppeoooooooooooo")
            if move.picking_id.sale_id.order_line[0].product_id:
                bom, bom_line = (
                    move.picking_id.sale_id.order_line[0]
                    .product_id.bom_ids[0]
                    .explode(move.product_id, 3)
                )
                print(bom, ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;")
                print(bom_line, "((((((((((()))))))))))")

            # order_line = next(
            #     (
            #         order_line
            #         for order_line in record.sale_id.order_line
            #         if order_line.product_id.id == move.product_id.id
            #     ),
            #     None,
            # )
            # if not order_line:
            #     continue
            # quantity_done = move.quantity_done
            # order_line_binding = order_line.woo_bind_ids[0]
            # price_unit = float(order_line_binding.price_unit)
            # total_tax_line = float(order_line_binding.total_tax_line)

            # if quantity_done > order_line_binding.product_uom_qty:
            #     raise MappingError(
            #         _(
            #             "Quantity done of move line is greater than quantity in "
            #             "WooCommerce Product Quantity."
            #         )
            #     )

            # divided_tax = total_tax_line / order_line_binding.product_uom_qty

            list_item = {
                "id": "12",
                "quantity": 3,
                "product_id": record.sale_id.order_line[0]
                .product_id.woo_bind_ids[0]
                .external_id,
                "refund_total": record.sale_id.order_line[0].price_subtotal,
                "refund_tax": [
                    {
                        "id": str(move.id),
                        "refund_total": record.sale_id.order_line[0].price_subtotal,
                    }
                ],
            }
            # total_amount += (price_unit + divided_tax) * quantity_done
            line_items.append(list_item)
        return_reason_text = html2plaintext(record.return_reason or "")
        return_data = {
            "order_id": record.sale_id.woo_bind_ids[0].external_id,
            "amount": str(record.sale_id.order_line[0].price_subtotal),
            "line_items": line_items,
            "api_refund": False,
        }
        if return_reason_text:
            return_data["reason"] = return_reason_text
        return return_data
