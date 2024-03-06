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
        already_process_grouped_product = []
        quantity = 0  # Initialize quantity variable
        prev_product = None  # Variable to store the previous product
        for move in record.move_ids:
            if move.sale_line_id.product_id in already_process_grouped_product:
                continue

            if move.picking_id.sale_id.order_line:
                sale_order_line = move.picking_id.sale_id.order_line[0]
                product_id = sale_order_line.product_id
                if product_id:
                    bom, bom_lines = product_id.bom_ids[0].explode(
                        product_id, move.sale_line_id.product_uom_qty
                    )
                    print(bom, ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;")
                    print(bom_lines, "((((((((((()))))))))))")
                    for line, line_data in bom_lines:
                        print(line)
                        print(line_data)
                    # Here, if move contains the product which is there in bom_lines
                    # and its quantity is less than or equal to qty present in move
                    # then it should increase the count by one
                    # for line in bom_lines:
                    #     print(line, "lllllllllllllllmmmmmmmmmmmmmmmmmm")
                    #     if (
                    #         line[1]["product"] == move.product_id
                    #         and line[1]["qty"] <= move.product_qty
                    #     ):
                            # if (
                            #     prev_product == move.sale_line_id.product_id
                            # ):  # Check if it's the same product as previous
                            #     continue  # Skip counting if it's the same product
                            # print("dededeeeeededeedededededdedededededdedededded")
                            # quantity += 1  # Increment quantity
                            # prev_product = move.sale_line_id.product_id  # Update previous product
                            # Do something else if needed
                    # already_process_grouped_product.append(move.sale_line_id.product_id)
        # print("Total Quantity:", quantity)  # Print total quantity after the loop

    # @mapping
    # def quantity_and_amount(self, record):
    #     """Mapping for Quantity and Amount"""
    #     line_items = []
    #     total_amount = 0.00
    #     sale_order_products = {
    #         order_line.product_id for order_line in record.sale_id.order_line
    #     }
    #     print(sale_order_products, "llllllllllllllllll sale_order_products")
    #     already_process_grouped_product = []
    #     for move in record.move_ids:
    #         # import pdb; pdb.set_trace()
    #         # if move.product_id.id not in sale_order_products:
    #         #     continue
    #         print(move.picking_id.sale_id.order_line[0].product_id, "ppeoooooooooooo")
    #         if move.sale_line_id.product_id in already_process_grouped_product:
    #             continue

    #         if move.picking_id.sale_id.order_line[0].product_id:
    #             bom, bom_lines = (
    #                 move.picking_id.sale_id.order_line[0]
    #                 .product_id.bom_ids[0]
    #                 .explode(move.product_id, move.sale_line_id.product_uom_qty)
    #             )
    #             print(bom, ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;")
    #             print(bom_lines, "((((((((((()))))))))))")
    #         list_item = {
    #             "id": "12",
    #             "quantity": 3,
    #             "product_id": record.sale_id.order_line[0]
    #             .product_id.woo_bind_ids[0]
    #             .external_id,
    #             "refund_total": record.sale_id.order_line[0].price_subtotal,
    #             "refund_tax": [
    #                 {
    #                     "id": str(move.id),
    #                     "refund_total": record.sale_id.order_line[0].price_subtotal,
    #                 }
    #             ],
    #         }
    #         # total_amount += (price_unit + divided_tax) * quantity_done
    #         line_items.append(list_item)
    #     return_reason_text = html2plaintext(record.return_reason or "")
    #     return_data = {
    #         "order_id": record.sale_id.woo_bind_ids[0].external_id,
    #         "amount": str(record.sale_id.order_line[0].price_subtotal),
    #         "line_items": line_items,
    #         "api_refund": False,
    #     }
    #     if return_reason_text:
    #         return_data["reason"] = return_reason_text
    #     return return_data

    # @mapping
    # def quantity_and_amount(self, record):
    #     """Mapping for Quantity and Amount"""
    #     line_items = []
    #     # total_amount = 0.00
    #     sale_order_products = {
    #         order_line.product_id for order_line in record.sale_id.order_line
    #     }
    #     print(sale_order_products, "llllllllllllllllll sale_order_products")
    #     already_process_grouped_product = []
    #     for move in record.move_ids:
    #         print(move.picking_id.sale_id.order_line[0].product_id, "ppeoooooooooooo")
    #         if move.sale_line_id.product_id in already_process_grouped_product:
    #             continue

    #         list_item = {
    #             "id": "12",
    #             "quantity": 3,
    #             "product_id": record.sale_id.order_line[0]
    #             .product_id.woo_bind_ids[0]
    #             .external_id,
    #             "refund_total": record.sale_id.order_line[0].price_subtotal,
    #             "refund_tax": [
    #                 {
    #                     "id": str(move.id),
    #                     "refund_total": record.sale_id.order_line[0].price_subtotal,
    #                 }
    #             ],
    #         }
    #         # total_amount += (price_unit + divided_tax) * quantity_done
    #         line_items.append(list_item)
    #     return_reason_text = html2plaintext(record.return_reason or "")
    #     return_data = {
    #         "order_id": record.sale_id.woo_bind_ids[0].external_id,
    #         "amount": str(record.sale_id.order_line[0].price_subtotal),
    #         "line_items": line_items,
    #         "api_refund": False,
    #     }
    #     if return_reason_text:
    #         return_data["reason"] = return_reason_text
    #     return return_data
