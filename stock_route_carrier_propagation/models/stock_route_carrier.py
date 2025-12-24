from odoo import fields, models


class StockRoute(models.Model):
    _inherit = "stock.route"

    carrier_id = fields.Many2one(
        "delivery.carrier",
        string="Default Delivery Carrier",
        help="Default delivery carrier for operations generated using this route.",
    )


class StockPicking(models.Model):
    _inherit = "stock.move"

    def _get_new_picking_values(self):
        """
        Extend picking values to include carrier from route
        """
        vals = super(StockPicking, self)._get_new_picking_values()
        carrier = self.rule_id.route_id.carrier_id
        if carrier:
            vals["carrier_id"] = carrier.id

        return vals
