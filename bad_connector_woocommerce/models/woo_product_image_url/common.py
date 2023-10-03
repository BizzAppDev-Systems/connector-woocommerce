from odoo import fields, models


class WooProductImageUrl(models.Model):
    _name = "woo.product.image.url"
    _description = "WooCommerce Product Image URL"

    name = fields.Char(required=True)
    url = fields.Char(string="URL")
    description = fields.Html(string="Description", translate=True)
