from odoo import fields, models


class StockRoute(models.Model):
    _inherit = "stock.route"

    carrier_id = fields.Many2one(
        "delivery.carrier",
        string="Default Delivery Carrier",
        help="Default delivery carrier for operations created using this route.",
    )
