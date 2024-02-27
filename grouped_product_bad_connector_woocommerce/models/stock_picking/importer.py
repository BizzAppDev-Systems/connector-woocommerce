import logging

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class WooStockPickingRefundImporter(Component):
    _inherit = "woo.stock.picking.refund.importer"

    def _get_return_pickings(self, original_pickings):
        """Retrieve information about return pickings based on original pickings."""
        to_return_moves = {}
        all_return_move = []
        for line in self.remote_record.get("line_items", []):
            original_quantity = abs(line.get("quantity"))
            binder = self.binder_for(model="woo.product.product")
            product_id = binder.to_internal(line.get("product_id"), unwrap=True)
            product_ids = []
            if product_id.bom_ids:
                for bom_lines in product_id.bom_ids.filtered(
                    lambda x: x.type == "phantom"
                ).bom_line_ids:
                    product_ids.append(bom_lines.product_id.id)
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
                to_return_moves = self._find_original_moves(
                    original_pickings, product_id.id, original_quantity
                )
                line_id = line.get("id")
                all_return_move.append(
                    {
                        "move": to_return_moves,
                        "product_id": product_id.id,
                        "line_id": line_id,
                    }
                )
        return all_return_move
