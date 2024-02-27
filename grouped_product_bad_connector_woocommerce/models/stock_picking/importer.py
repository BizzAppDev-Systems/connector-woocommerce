import logging
from copy import deepcopy

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class WooStockPickingRefundImporter(Component):
    _inherit = "woo.stock.picking.refund.importer"

    # def _find_original_moves(self, pickings, product_id, return_qty):
    #     """Find original moves associated with a product for return."""
    #     moves = pickings.move_ids.filtered(
    #         lambda move: move.product_id.id == product_id
    #     )
    #     remaining_moves = {}
    #     for move in moves:
    #         returned_qty = move.returned_move_ids.mapped("product_qty")
    #         if returned_qty:
    #             remaining_qty = move.product_qty - returned_qty[0]
    #             if remaining_qty == 0:
    #                 continue
    #             remaining_moves[move] = remaining_qty
    #         else:
    #             remaining_moves[move] = move.product_qty
    #     to_return_moves = {}
    #     for remaining_move, remaining_qty in remaining_moves.items():
    #         if return_qty < remaining_qty:
    #             to_return_moves[remaining_move] = return_qty
    #             break
    #         else:
    #             to_return_moves[remaining_move] = remaining_qty
    #             return_qty -= remaining_qty
    #             continue
    #     to_return_moves = {k: v for k, v in to_return_moves.items() if v != 0.0}
    #     return to_return_moves

    # def _update_return_line(self, return_line, quantity, move_external_id):
    #     """Update the return line."""
    #     return_line.update(
    #         {
    #             "quantity": quantity,
    #             "move_external_id": move_external_id,
    #         }
    #     )

    # def _process_return_moves(self, to_return_moves, returns):
    #     """Process return moves and update return lines."""
    #     moves = [(6, 0, [])]
    #     for returned in returns:
    #         if not returned[-1] or "move_external_id" not in returned[-1]:
    #             continue
    #         new_return = deepcopy(returned)
    #         self._update_return_line(
    #             new_return[-1],
    #             new_return[-1]["quantity"],
    #             new_return[-1]["move_external_id"],
    #         )
    #         moves.append(new_return)
    #     return moves

    def _get_return_pickings(self, original_pickings):
        """Retrieve information about return pickings based on original pickings."""
        to_return_moves = {}
        all_return_move = []
        for line in self.remote_record.get("line_items", []):
            original_quantity = abs(line.get("quantity"))
            binder = self.binder_for(model="woo.product.product")
            product_id = binder.to_internal(line.get("product_id"), unwrap=True)
            # if product_id.bom_ids.type == "kit":
            print(
                product_id, "............................................... product_id"
            )
            print(
                product_id.bom_ids, "................................product_id.bom_ids"
            )
            print(product_id.name,"..............................product name")
            print(product_id.bom_ids.type,";;;;;;;;;;;;;;;;;;;;;; .............. product_id.bom_ids.type")
            if product_id.bom_ids.type == "kit":
                print("yessssssssss")
                for bom_lines in product_id.bom_ids.filtered(
                    lambda x: x.type == "kit"
                ).bom_line_ids:
                    # Collect product IDs from BOM lines
                    product_ids = [bom_line.product_id.id for bom_line in bom_lines]
                    print(product_ids, ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;")
                    # Now you have all the product IDs associated with the BOM lines
                    # You can use these product IDs as needed in your code
                    print("Products associated with BOM lines:", product_ids)
                if product_ids:
                    for product_id in product_ids:
                        to_return_moves = self._find_original_moves(
                            original_pickings, product_id, original_quantity
                        )
                        line_id = line.get("id")
                        all_return_move.append(
                            {
                                "move": to_return_moves,
                                "product_id": product_id,
                                "line_id": line_id,
                            }
                        )
            else:
                # product_id = binder.to_internal(line.get("product_id"), unwrap=True).id
                to_return_moves = self._find_original_moves(
                    original_pickings, product_id.id, original_quantity
                )
                line_id = line.get("id")
                all_return_move.append(
                    {
                        "move": to_return_moves,
                        "product_id": product_id,
                        "line_id": line_id,
                    }
                )
        return all_return_move

    # def _process_return_picking(self, picking_moves_dict):
    #     """Process return picking based on the provided picking moves dictionary."""
    #     delivery_order = next(iter(picking_moves_dict))
    #     return_wizard = (
    #         self.env["stock.return.picking"]
    #         .with_context(active_id=delivery_order.id, active_model="stock.picking")
    #         .new({})
    #     )
    #     self.env["stock.return.picking"].with_context(
    #         active_ids=delivery_order.ids,
    #         active_id=delivery_order.ids[0],
    #         active_model="stock.picking",
    #     )
    #     return_wizard._onchange_picking_id()
    #     for picking_move in picking_moves_dict[delivery_order]:
    #         return_line = return_wizard.product_return_moves.filtered(
    #             lambda r: r.product_id.id == picking_move.get("product_id")
    #         )
    #         self._update_return_line(
    #             return_line,
    #             picking_move.get("quantity"),
    #             picking_move.get("line_id"),
    #         )
    #     picking_returns = return_wizard._convert_to_write(
    #         {name: return_wizard[name] for name in return_wizard._cache}
    #     )
    #     picking_returns["product_return_moves"] = self._process_return_moves(
    #         picking_moves_dict, picking_returns["product_return_moves"]
    #     )
    #     picking_returns["return_reason"] = self.remote_record.get("reason")
    #     stock_return_picking = self.env["stock.return.picking"].create(picking_returns)
    #     return_id, return_type = stock_return_picking._create_returns()
    #     return picking_returns, return_id

    # def _create(self, data):
    #     """Create a refund for the WooCommerce stock picking in Odoo."""
    #     binder = self.binder_for(model="woo.sale.order")
    #     sale_order = binder.to_internal(self.remote_record.get("order_id"), unwrap=True)
    #     if not sale_order:
    #         raise ValidationError(
    #             _(
    #                 "Sale order is missing for order_id: %s"
    #                 % self.remote_record.get("order_id")
    #             )
    #         )
    #     if not sale_order.picking_ids.filtered(lambda picking: picking.state == "done"):
    #         raise ValidationError(
    #             _(
    #                 "The delivery order has not been validated, therefore, we cannot "
    #                 "proceed with the creation of the return available."
    #             )
    #         )
    #     original_pickings = sale_order.picking_ids.filtered(
    #         lambda picking: picking.picking_type_id.code == "outgoing"
    #     )
    #     to_return_moves = self._get_return_pickings(original_pickings)
    #     return_picking_data = {}
    #     for to_return_move in to_return_moves:
    #         picking_id = None
    #         line_id_counter = {}
    #         for move, quantity in to_return_move["move"].items():
    #             picking_id = move.picking_id
    #             if picking_id not in return_picking_data:
    #                 return_picking_data[picking_id] = {
    #                     "product_moves": [],
    #                     "line_id_counter": line_id_counter,
    #                 }
    #             line_id_base = to_return_move["line_id"]
    #             if line_id_base not in line_id_counter:
    #                 line_id_counter[line_id_base] = 0
    #             line_id_counter[line_id_base] += 1
    #             line_id = f"{line_id_base}_{line_id_counter[line_id_base]}"
    #             return_picking_data[picking_id]["product_moves"].append(
    #                 {
    #                     "move": move,
    #                     "product_id": to_return_move["product_id"],
    #                     "quantity": quantity,
    #                     "line_id": line_id,
    #                 }
    #             )
    #     picking_moves = []
    #     for picking_id, value in return_picking_data.items():
    #         product_ids = list({move["product_id"] for move in value["product_moves"]})
    #         picking_data = {}
    #         picking_data[picking_id] = value["product_moves"]
    #         picking_data["product_ids"] = product_ids
    #         picking_moves.append(picking_data)
    #     picking_bindings = self.env["woo.stock.picking.refund"]
    #     for picking in picking_moves:
    #         (
    #             picking_returns,
    #             return_id,
    #         ) = self._process_return_picking(
    #             picking,
    #         )
    #         data["odoo_id"] = return_id
    #         res = super(WooStockPickingRefundImporter, self)._create(data)
    #         picking_bindings |= res
    #         for product_id in picking.get("product_ids"):
    #             picking = next(iter(picking))
    #             self._check_lot_tracking(product_id, picking, return_id)
    #     return picking_bindings

    # def _after_import(self, binding, **kwargs):
    #     """
    #     Inherit Method: inherit method to check if the refund order status is
    #     'refunded'. If so, it updates the corresponding sale order's status to
    #     'refunded' in the local system, if the delivered quantity of all order lines is
    #     not zero.
    #     """
    #     res = super(WooStockPickingRefundImporter, self)._after_import(
    #         binding, **kwargs
    #     )
    #     line_items = self.remote_record.get("line_items")
    #     product_id_map = {item["product_id"]: item["id"] for item in line_items}
    #     if not self.backend_record.process_return_automatically:
    #         return res
    #     for bind in binding:
    #         for move in bind.odoo_id.move_ids:
    #             move.external_move = product_id_map[
    #                 int(move.product_id.woo_bind_ids.external_id)
    #             ]
    #             move.quantity_done = move.product_uom_qty
    #         bind.odoo_id.button_validate()
    #     if self.remote_record.get("refund_order_status") != "refunded":
    #         return res

    #     self.env["stock.picking"]._update_order_status()
    #     return res
