from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_new_picking_values(self):
        vals = super(StockMove, self)._get_new_picking_values()
        # Check if any move has a carrier_id from the route
        carrier_id = self.mapped("rule_id.route_id.carrier_id.id")
        # If we have a carrier from the route, set it on the picking
        if carrier_id and carrier_id[0]:
            vals["carrier_id"] = carrier_id[0]
        return vals
