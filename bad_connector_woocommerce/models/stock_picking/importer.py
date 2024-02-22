import logging
from copy import deepcopy

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class WooStockPickingRefundBatchImporter(Component):
    _name = "woo.stock.picking.refund.batch.importer"
    _inherit = "woo.delayed.batch.importer"
    _apply_on = "woo.stock.picking.refund"


class WooStockPickingRefundImportMapper(Component):
    _name = "woo.stock.picking.refund.import.mapper"
    _inherit = "woo.import.mapper"
    _apply_on = "woo.stock.picking.refund"


class WooStockPickingRefundImporter(Component):
    _name = "woo.stock.picking.refund.importer"
    _inherit = "woo.importer"
    _apply_on = "woo.stock.picking.refund"

    def _must_skip(self):
        """Skipped Record which are already imported."""
        if self.binder.to_internal(self.external_id):
            return _("Already imported")
        return super(WooStockPickingRefundImporter, self)._must_skip()

    def _get_remote_data(self, **kwargs):
        """Retrieve remote data related to an refunded order."""
        attributes = {}
        attributes["order_id"] = kwargs.get("order_id")
        data = self.backend_adapter.read(self.external_id, attributes=attributes)
        if not data.get(self.backend_adapter._woo_ext_id_key):
            data[self.backend_adapter._woo_ext_id_key] = self.external_id
        data["refund_order_status"] = kwargs["refund_order_status"]
        return data

    def _check_lot_tracking(self, product_id, delivery_order, return_id):
        """
        Check if lot tracking is consistent between the original delivery order and
        the return picking.
        """
        product = self.env["product.product"].browse(product_id)
        picking_id = self.env["stock.picking"].browse([return_id])
        if product.tracking == "lot":
            original_move = delivery_order.move_ids.filtered(
                lambda move: move.product_id.id == product_id
            )
            original_lots = original_move.mapped("move_line_ids.lot_id")
            return_lots = picking_id.move_ids.mapped("move_line_ids.lot_id")
            original_lots = set(original_lots)
            return_lots = set(return_lots)
            if not return_lots.issubset(original_lots):
                message = (
                    "Lot differ from original delivery order so please verify and "
                    "validate manually for product: %s." % (product.name)
                )
                _logger.info(message)
                user_id = delivery_order.user_id or self.backend_record.activity_user_id
                self.env["woo.backend"].create_activity(
                    record=picking_id,
                    message=message,
                    activity_type="mail.mail_activity_data_warning",
                    user=user_id,
                )
                return False
        return True

    def _find_original_moves(self, pickings, product_id, return_qty):
        # Function to find original moves for a product in pickings
        print(
            pickings,
            "pickingspickingspickingspickingspickingspickings pickingspickings",
        )
        moves = pickings.move_ids.filtered(
            lambda move: move.product_id.id == product_id
        )
        remaining_moves = {}
        for move in moves:
            returned_qty = move.returned_move_ids.mapped("product_qty")
            if returned_qty:
                remaining_qty = move.product_qty - returned_qty[0]
                if remaining_qty == 0:
                    continue
                remaining_moves[move] = remaining_qty
            else:
                remaining_moves[move] = move.product_qty

        to_return_moves = {}
        for remaining_move, remaining_qty in remaining_moves.items():
            if return_qty < remaining_qty:
                print(return_qty)
                to_return_moves[remaining_move] = return_qty
                break
            else:
                to_return_moves[remaining_move] = remaining_qty
                return_qty -= remaining_qty
                continue
        to_return_moves = {k: v for k, v in to_return_moves.items() if v != 0.0}
        print(to_return_moves, "after removeeeeeeeeeeeeeeeeeeeeeeeeee")
        return to_return_moves

    def _update_return_line(self, return_line, quantity, move_external_id):
        return_line.update(
            {
                "quantity": quantity,
                "move_external_id": move_external_id,
            }
        )

    def _process_return_moves(self, to_return_moves, returns):
        # Process return moves for product quantities
        moves = [(6, 0, [])]
        for returned in returns:
            print(returned[-1], ";;;;;;;;;;;;; returns returns returns returns returns")
            if not returned[-1]:
                print("hereeeeeeeeeeeeee")
                continue
            # product_id = returns[-1]["product_id"]
            print(returned, ";;;;;;;;;;;;; returns returns returns returns returns")
            print(
                to_return_moves,
                ";;;;;;;;to_return_moves to_return_moves to_return_moves  to_return_moves",
            )
            for move, qty in to_return_moves.get("move").items():
                new_return = deepcopy(returned)
                line_id = to_return_moves.get("line_id")
                print(
                    new_return[-1], ";;;;;;;;;;;;;;; its new_return[-1] new_return[-1] "
                )
                self._update_return_line(new_return[-1], qty, line_id)
                moves.append(new_return)
        return moves

    def _get_eligible_pickings(self, original_pickings):
        to_return_moves = {}
        all_return_move = []
        for line in self.remote_record.get("line_items", []):
            original_quantity = abs(line.get("quantity"))
            binder = self.binder_for(model="woo.product.product")
            product_id = binder.to_internal(line.get("product_id"), unwrap=True).id
            to_return_moves = self._find_original_moves(
                original_pickings, product_id, original_quantity
            )
            line_id = line.get("id")
            all_return_move.append(
                {
                    "line": line_id,
                    "move": to_return_moves,
                    "product_id": product_id,
                    "line_id": line_id,
                }
            )
        print(
            all_return_move,
            "all_return_move all_return_move all_return_move all_return_move",
        )
        return all_return_move

    def _process_return_picking(self, delivery_order, picking_moves_dict):
        print(picking_moves_dict, ";;;;;;;;;;;;;;;;;;;;;;;;; to_return_moves")
        print(
            delivery_order,
            "delivery_order delivery_order delivery_order delivery_order",
        )
        product_id = picking_moves_dict.get("product_id")
        return_wizard = (
            self.env["stock.return.picking"]
            .with_context(active_id=delivery_order.id, active_model="stock.picking")
            .new({})
        )
        self.env["stock.return.picking"].with_context(
            active_ids=delivery_order.ids,
            active_id=delivery_order.ids[0],
            active_model="stock.picking",
        )
        return_wizard._onchange_picking_id()
        for move_key, move_value in picking_moves_dict["move"].items():
            return_line = return_wizard.product_return_moves.filtered(
                lambda r: r.product_id.id == product_id
            )
            print(return_line, "return_line return_linereturn_line return_line")
            if return_line:
                self._update_return_line(
                    return_line,
                    move_value,
                    picking_moves_dict.get("line_id"),
                )
            print(
                return_wizard, "return_wizard return_wizardreturn_wizard return_wizard"
            )
            print(
                return_wizard._cache,
                "return_wizard._cache return_wizard._cache return_wizard._cache",
            )
            picking_returns = return_wizard._convert_to_write(
                {name: return_wizard[name] for name in return_wizard._cache}
            )
            print(
                picking_returns["product_return_moves"], "cccccccccccccccccccccccccccc"
            )
            picking_returns["product_return_moves"] = self._process_return_moves(
                picking_moves_dict, picking_returns["product_return_moves"]
            )
            picking_returns["return_reason"] = self.remote_record.get("reason")
            stock_return_picking = self.env["stock.return.picking"].create(
                picking_returns
            )
            print(stock_return_picking, "stock_return_picking stock_return_picking")
            # print(return_type,"return_type return_type return_type return_type")
            return_id, return_type = stock_return_picking._create_returns()
            print(
                return_type, "return_typereturn_typereturn_typereturn_typereturn_type"
            )
        # return picking_returns, return_id
        return picking_returns, return_id, product_id

    def _create(self, data):
        binder = self.binder_for(model="woo.sale.order")
        sale_order = binder.to_internal(self.remote_record.get("order_id"), unwrap=True)
        if not sale_order:
            raise ValidationError(
                _(
                    "Sale order is missing for order_id: %s"
                    % self.remote_record.get("order_id")
                )
            )
        if not sale_order.picking_ids.filtered(lambda picking: picking.state == "done"):
            raise ValidationError(
                _(
                    "The delivery order has not been validated, therefore, we cannot "
                    "proceed with the creation of the return available."
                )
            )
        original_pickings = sale_order.picking_ids.filtered(
            lambda picking: picking.picking_type_id.code == "outgoing"
        )
        eligible_moves = self._get_eligible_pickings(original_pickings)
        for move_data in eligible_moves:
            move = move_data["move"]
            for picking in original_pickings:
                if any(move in picking.move_ids for move in move.keys()):
                    move_data["picking_id"] = picking
                    break
        print(
            eligible_moves,
            "pickings_moves_map >>>>,,,,,,<<<,,,<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>",
        )
        picking_bindings = self.env["woo.stock.picking.refund"]
        for picking in eligible_moves:
            print(picking, "picking picking")
            (
                picking_returns,
                return_id,
                product_id,
            ) = self._process_return_picking(
                picking.get("picking_id"),
                picking,
            )
            data["odoo_id"] = return_id
            res = super(WooStockPickingRefundImporter, self)._create(data)
            # picking_bindings |= res
            self._check_lot_tracking(product_id, picking, return_id)
        return res
        # return picking_bindings

    # def _create(self, data):
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
    #                 "The delivery order has not been validated, therefore, we cannot proceed with the creation of the return available."
    #             )
    #         )

    #     product_grouped_qty = {}
    #     original_pickings = sale_order.picking_ids.filtered(
    #         lambda picking: picking.picking_type_id.code == "outgoing"
    #     )
    #     (
    #         eligible_moves,
    #         product_id,
    #         original_quantity,
    #         line_id,
    #     ) = self._get_eligible_pickings(original_pickings, product_grouped_qty)
    #     repeated_product = {}

    #     # picking_bindings = self.env["woo.stock.picking.refund"]
    #     print(
    #         eligible_moves,
    #         "eligible_moves eligible_moves eligible_moves eligible_moves eligible_moves",
    #     )
    #     # for move in eligible_moves:
    #         # eligible_pickings = (
    #         #     self.env["stock.move"]
    #         #     .browse([move.id for move in move.keys()])
    #         #     .mapped("picking_id")
    #         # )
    #         # print(
    #         #     eligible_pickings,
    #         #     "gggggggggggggggggggggggggggggggggggggggggggggggggggg",
    #         # )
    #         # eligible_pickings = eligible_moves.mapped("picking_id")
    #         # for delivery_order in eligible_pickings:
    #         # print(delivery_order, "delivery_orderrrrrrrrrrrrrr")
    #         # to_return_moves = [
    #         #     (k, v) for k, v in move.items() if k.picking_id == delivery_order
    #         # ]
    #         # picking_returns, return_id = self._process_return_picking(delivery_order)
    #         # print(
    #         #     "to_return_movesto_return_movesto_return_movesto_return_movesto_return_moves",
    #         #     to_return_moves,
    #         # )
    #         for to_return_moves in eligible_moves:
    #             (
    #                 picking_returns,
    #                 return_id,
    #                 product_id,
    #             ) = self._process_return_picking(
    #                 delivery_order,
    #                 repeated_product,
    #                 to_return_moves,
    #                 product_id,
    #                 original_quantity,
    #                 line_id,
    #             )
    #             data["odoo_id"] = return_id
    #             # if count > 0:
    #             #     data['external_id'] =
    #             res = super(WooStockPickingRefundImporter, self)._create(data)
    #             # picking_bindings |= res
    #             self._check_lot_tracking(product_id, delivery_order, return_id)
    #     # print(
    #     #     picking_bindings,
    #     #     ";;;;;;;;;;;;;;;;;;;;;;;;;;; picking_bindingspicking_bindings",
    #     # )
    #     # for bind in picking_bindings:
    #     #     if not bind.external_id:
    #     #         bind.external_id = self.external_id
    #     # return picking_bindings
    #     return res
    # I want to implement the code in such a way that we get eligible_moves as list of dictory example
    # [{stock.move(123):2.0,stock.move(234):3.0},{stock.move(423):1.0,stock.move(934):2.0}]
    # where in each dic move is belongs to different picking so from this generated list of dic i want
    # to make another list of dic which contain the moves which belongs to that perticular picking
    # means  {stock.move(123):2.0,stock.move(234):3.0} dic move is belong to one picking

    def _after_import(self, binding, **kwargs):
        """
        Inherit Method: inherit method to checks if the refund order status is
        'refunded'. If so, it updates the corresponding sale order's status to
        'refunded' in the local system, if the delivered quantity of all order lines is
        not zero.
        """
        res = super(WooStockPickingRefundImporter, self)._after_import(
            binding, **kwargs
        )
        if not self.backend_record.process_return_automatically:
            return res
        print(binding, ";;;;;;;;;;;; binding.odoo_id")
        # print(
        #     binding[0].external_id,
        #     ";;;;;;;;;;;; bindiiinnnnnnnnnngggggggggggggg external_id",
        # )
        # print(
        #     binding[1].external_id,
        #     ";;;;;;;;;;;; bindiiinnnnnnnnnngggggggggggggg external_id11111",
        # )
        # for bind in binding:
        # print(bind.external_id, "bindiiinnnnnnnnnngggggggggggggg")
        validated_pickings = binding.odoo_id.sale_id.picking_ids.filtered(
            lambda p: p.picking_type_id.code == "incoming"
            and p.state != "done"
            and p.woo_return_bind_ids
        )
        for picking in validated_pickings:
            # print(
            #     validated_pickings,
            #     "validated_pickingsvalidated_pickingsvalidated_pickings",
            # )
            # for picking in validated_pickings:
            print(picking, ";;;;;;;;;;; picking ")
            for move in picking.move_ids:
                move.quantity_done = move.product_uom_qty
            picking.button_validate()
            # picking = binding.odoo_id
            # for move in picking.move_ids:
            #     move.quantity_done = move.product_uom_qty

            # picking.button_validate()
        print(
            self.remote_record.get("refund_order_status"),
            "self.remote_record.get(refund_order_status)",
        )
        if self.remote_record.get("refund_order_status") != "refunded":
            print("helooooooooooooooooooooooooo i m not refunded")
            return res
        self.env["stock.picking"]._update_order_status()
        return res
