import logging
from copy import deepcopy
from collections import defaultdict

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

    def _create(self, data):
        """
        Inherit Method: inherit method to creates a return for a WooCommerce sale
        order in Odoo.
        """
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
        eligible_pickings = set()
        product_grouped_qty = {}
        original_pickings = sale_order.picking_ids.filtered(
            lambda picking: picking.picking_type_id.code == "outgoing"
        )
        print(
            original_pickings,
            ";aaaaaaaaaa original_pickingsoriginal_pickingsoriginal_pickingsoriginal_pickings",
        )
        print(self.remote_record, "remote_recordremote_recordremote_record")
        # remaining_quantity = 0
        for line in self.remote_record.get("line_items", []):
            quantity = abs(line.get("quantity"))
            print(line, "line line line line line")
            print(line.get("product_id"), ";;;;;;;;; line product id")
            binder = self.binder_for(model="woo.product.product")
            product_id = binder.to_internal(line.get("product_id"), unwrap=True).id
            if product_id not in product_grouped_qty:
                product_grouped_qty[product_id] = 0
            product_grouped_qty[product_id] += quantity
            print(quantity, "quantityyyyyyyyyy")
            print(
                product_grouped_qty,
                "quantityquantityquantityquantityquantityquantityquantity",
            )
            for picking in original_pickings:
                print(product_grouped_qty, ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;")
                if picking.move_ids.filtered(
                    lambda move: move.product_id.id == product_id
                    and move.product_uom_qty == quantity
                ):
                    # picking_move.product_uom_qty -= quantity
                    print(";;;;;;;;;;;;;;;;; here before break")
                    print("before addding the picking update the quantity")
                    print(product_grouped_qty[product_id], "updated the quantity")
                    eligible_pickings.add(picking)
                    print("breakkkkkkkkkkkkkkkkkkkkkkk picking")
                    break
                elif picking.move_ids.filtered(
                    lambda move: move.product_id.id == product_id
                    and move.product_uom_qty < quantity
                ):
                    filtered_move = picking.move_ids.filtered(
                        lambda move: move.product_id.id == product_id
                        and move.product_uom_qty < quantity
                    )
                    # Update the quantity
                    quantity = quantity - filtered_move.product_uom_qty
                    print(
                        product_grouped_qty[product_id],
                        "product_grouped_qty[product_id]product_grouped_qty[product_id]",
                    )
                    print(quantity, "its a quantity in < condition")
                    print("hereeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
                    print(
                        product_grouped_qty[product_id], ";;;;;;;;; here in <<<<<<,<<"
                    )
                    print(quantity, "quantityquantityquantityquantityquantityquantity")
                    eligible_pickings.add(picking)
                    if quantity == 0:
                        break
                    continue
                elif picking.move_ids.filtered(
                    lambda move: move.product_id.id == product_id
                    and move.product_uom_qty > quantity
                ):
                    filtered_move = picking.move_ids.filtered(
                        lambda move: move.product_id.id == product_id
                        and move.product_uom_qty > quantity
                    )
                    quantity = filtered_move.product_uom_qty - quantity
                    eligible_pickings.add(picking)
                    if quantity == 0:
                        break
                    continue
                else:
                    continue
            print("--------------------------------------------continue")
        print(
            eligible_pickings,
            "eligible_pickingseligible_pickingseligible_pickingseligible_pickings",
        )
        if not eligible_pickings:
            raise ValidationError(
                _(
                    "No eligible pickings found for return creation for sale order with ID: %s"
                    % sale_order.id
                )
            )
        for delivery_order in eligible_pickings:
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
            binder = self.binder_for(model="woo.product.product")
            product_grouped_qty = {}
            product_return_qty = {}
            for line in self.remote_record.get("line_items"):
                quantity = abs(line.get("quantity"))
                product_id = binder.to_internal(line.get("product_id"), unwrap=True).id
                if product_id not in product_grouped_qty:
                    product_grouped_qty[product_id] = 0
                product_grouped_qty[product_id] += quantity
                if product_id not in product_return_qty:
                    product_return_qty[product_id] = []
                product_return_qty[product_id].append([line.get("id"), quantity])
                return_line = return_wizard.product_return_moves.filtered(
                    lambda r: r.product_id.id == product_id
                )
                if return_line:
                    print(return_line, "retuuuuuurrrrrrnnnnnnnn line")
                    if return_line.quantity == quantity:
                        print(
                            return_line.quantity, quantity, "equalllllllllllllllllllll"
                        )
                        return_line.update(
                            {
                                "quantity": float(product_grouped_qty[product_id]),
                                "move_external_id": line.get("id"),
                            }
                        )
                    elif return_line.quantity > quantity:
                        print(
                            return_line.quantity,
                            quantity,
                            "greaterrrrrrrrrrrrrrrrrrrrrrr",
                        )
                        return_line.update(
                            {
                                "quantity": quantity,
                                "move_external_id": line.get("id"),
                            }
                        )
                        product_grouped_qty[product_id] = quantity
                    elif return_line.quantity < quantity:
                        print(return_line.quantity, quantity, "lesssssssssssssssssssss")
                        return_line.update(
                            {
                                "quantity": return_line.quantity,
                                "move_external_id": line.get("id"),
                            }
                        )
                        product_grouped_qty[product_id] = return_line.quantity
            picking_returns = return_wizard._convert_to_write(
                {name: return_wizard[name] for name in return_wizard._cache}
            )
            moves = [(6, 0, [])]

            # Iterate over the returns in picking_returns["product_return_moves"]
            for returns in picking_returns["product_return_moves"]:
                if (
                    returns[-1] and "move_external_id" in returns[-1]
                ):  # Simplified condition
                    product_id = returns[-1]["product_id"]
                    for group_return in product_return_qty.get(product_id, []):
                        line_id, qty = group_return
                        new_return = deepcopy(returns)
                        print(new_return, "new_returnnew_return")

                        # Adjust the quantity based on conditions
                        if new_return[-1].get("quantity") == qty:
                            new_return[-1].update(
                                {"quantity": qty, "move_external_id": line_id}
                            )
                            qty = qty - new_return[-1].get("quantity")
                            print(new_return[-1].get("quantity"), qty, "its equallll")
                        elif new_return[-1].get("quantity") > qty:
                            new_return[-1].update(
                                {"quantity": qty, "move_external_id": line_id}
                            )
                            qty = new_return[-1].get("quantity") - qty
                            print(
                                new_return[-1].get("quantity"), qty, "its greaterrrrr"
                            )
                        elif new_return[-1].get("quantity") < qty:
                            new_return[-1].update(
                                {
                                    "quantity": new_return[-1].get("quantity"),
                                    "move_external_id": line_id,
                                }
                            )
                            qty = qty - new_return[-1].get("quantity")
                            print(new_return[-1].get("quantity"), qty, "its less")

                        # Append the modified new_return to moves
                        moves.append(new_return)
            # Update the "product_return_moves" in picking_returns
            picking_returns["product_return_moves"] = moves
            # Rest of your code remains unchanged
            picking_returns["return_reason"] = self.remote_record.get("reason")
            stock_return_picking = self.env["stock.return.picking"].create(
                picking_returns
            )
            return_id, return_type = stock_return_picking._create_returns()
            data["odoo_id"] = return_id
            res = super(WooStockPickingRefundImporter, self)._create(data)
            self._check_lot_tracking(product_id, delivery_order, return_id)
        return res

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
        validated_pickings = binding.odoo_id.sale_id.picking_ids.filtered(
            lambda p: p.woo_return_bind_ids
        )
        print(
            validated_pickings, "validated_pickingsvalidated_pickingsvalidated_pickings"
        )
        for picking in validated_pickings:
            for move in picking.move_ids:
                move.quantity_done = move.product_uom_qty

            picking.button_validate()
        # picking = binding.odoo_id
        # for move in picking.move_ids:
        #     move.quantity_done = move.product_uom_qty

        # picking.button_validate()
        if self.remote_record.get("refund_order_status") != "refunded":
            return res
        self.env["stock.picking"]._update_order_status()
        return res
