from odoo import fields, models


class WooDownloadableProduct(models.Model):
    _name = "woo.downloadable.product"
    _description = "WooCommerce Downloadable Product"

    name = fields.Char(string="File Name", required=True)
    url = fields.Char(string="File URL")
    file_id = fields.Char(string="File ID")
