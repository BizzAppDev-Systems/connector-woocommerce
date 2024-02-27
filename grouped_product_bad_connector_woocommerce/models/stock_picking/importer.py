import logging

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class WooStockPickingRefundImporter(Component):
    _inherit = "woo.stock.picking.refund.importer"

    def _get_return_pickings(self, original_pickings):
        """Retrieve information about return pickings based on original pickings."""
        return_moves = []
        for line in self.remote_record.get("line_items", []):
            original_quantity = abs(line.get("quantity"))
            binder = self.binder_for(model="woo.product.product")
            product_id = binder.to_internal(line.get("product_id"), unwrap=True)
            if product_id.bom_ids:
                product_ids = [
                    bom_line.product_id.id
                    for bom in product_id.bom_ids
                    if bom.type == "phantom"
                    for bom_line in bom.bom_line_ids
                ]
            else:
                product_ids = [product_id.id]
            for product_id in product_ids:
                to_return_moves = self._find_original_moves(
                    original_pickings, product_id, original_quantity
                )
                line_id = line.get("id")
                return_moves.append(
                    {
                        "move": to_return_moves,
                        "product_id": product_id,
                        "line_id": line_id,
                    }
                )
        return return_moves

    def _after_import(self, binding, **kwargs):
        """
        Inherit Method: inherit method to check if the refund order status is
        'refunded'. If so, it updates the corresponding sale order's status to
        'refunded' in the local system, if the delivered quantity of all order lines is
        not zero.
        """
        line_items = self.remote_record.get("line_items")
        product_id_map = {item["product_id"]: item["id"] for item in line_items}

        for move in binding.mapped('odoo_id.move_ids'):
            woo_product_id = move.product_id.woo_bind_ids.filtered(
                lambda a: a.backend_id == self.backend_record
            )
            if woo_product_id and int(woo_product_id.external_id) in product_id_map:
                continue
            woo_product_id = move.sale_line_id.product_id.woo_bind_ids.filtered(
                lambda a: a.backend_id == self.backend_record
            )
            move.external_move = product_id_map[int(woo_product_id.external_id)]
            move.quantity_done = move.product_uom_qty
        return super(WooStockPickingRefundImporter, self)._after_import(
            binding, **kwargs
        )
