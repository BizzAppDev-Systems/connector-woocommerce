from odoo import fields, models


class WooSaleStatus(models.Model):
    _name = "woo.sale.status"
    _description = "WooCommerce Sale Order Status"

    name = fields.Char(required=True)
    code = fields.Char(string="Status Code")
