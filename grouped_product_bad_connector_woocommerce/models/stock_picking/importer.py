import logging

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class WooStockPickingRefundImporter(Component):
    _inherit = "woo.stock.picking.refund.importer"

    def _get_return_pickings(self, original_pickings):
        """
        Overrides method: Retrieve information about return pickings based on
        original pickings for grouped products.
        """
        return_moves = []
        for line in self.remote_record.get("line_items", []):
            original_quantity = abs(line.get("quantity"))
            binder = self.binder_for(model="woo.product.product")
            product_id = binder.to_internal(line.get("product_id"), unwrap=True)
            line_id = line.get("id")
            if not product_id.bom_ids:
                to_return_moves = self._find_original_moves(
                    original_pickings, product_id.id, original_quantity
                )
                return_moves.append(
                    {
                        "move": to_return_moves,
                        "product_id": product_id.id,
                        "line_id": line_id,
                    }
                )
                continue
            for bom in product_id.bom_ids:
                boms, lines = bom.explode(product_id, original_quantity)
                for bom_line in lines:
                    move_product_id = bom_line[0].product_id
                    to_return_qty = bom_line[1]["qty"]
                    to_return_moves = self._find_original_moves(
                        original_pickings,
                        move_product_id.id,
                        to_return_qty,
                    )
                    return_moves.append(
                        {
                            "move": to_return_moves,
                            "product_id": move_product_id.id,
                            "line_id": line_id,
                        }
                    )
        return return_moves

    def _after_import(self, binding, **kwargs):
        """
        Inherit Method: inherit method to set external_move for grouped product.
        """
        line_items = self.remote_record.get("line_items")
        product_id_map = {item["product_id"]: item["id"] for item in line_items}
        for move in binding.mapped("odoo_id.move_ids"):
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
