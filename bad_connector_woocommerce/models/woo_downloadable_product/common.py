from odoo import fields, models


class WooProductImageUrl(models.Model):
    _name = "woo.downloadable.product"
    _description = "WooCommerce Downloadable Product"

    name = fields.Char(string="File Name", required=True)
    url = fields.Char(string="File URL", required=True)
    file_id = fields.Char(string="File ID", required=True)
