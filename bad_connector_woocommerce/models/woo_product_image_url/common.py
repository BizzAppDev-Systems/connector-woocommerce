import base64
from odoo import fields, models
from ...components.utils import fetch_image_data


class WooProductImageUrl(models.Model):
    _name = "woo.product.image.url"
    _inherit = "woo.binding"
    _apply_on = ["woo.product.product"]
    _usage = "product.image.importer"
    _description = "WooCommerce Product Image URL"

    name = fields.Char(required=True)
    url = fields.Char(string="URL")
    description = fields.Html(string="Description", translate=True)

    def run(self, external_id, image_data):
        if not image_data:
            return
        binding = self.env["woo.product.product"].browse(external_id)

        for index, image_info in enumerate(image_data):
            image_url = image_info.get("src")

            if image_url:
                binary_data = fetch_image_data(image_url)
                print(binary_data,"ppppaaaaaaaaaaaaaaaaaa")
                if binary_data:
                    if index == 0:
                        decoded_binary_data = base64.b64decode(binary_data)
                        binding.write({"image_1920": decoded_binary_data})
                    else:
                        self.env["woo.product.image.url"].create(
                            {
                                "name": image_info.get("name"),
                                "url": image_url,
                                "description": image_info.get("alt"),
                            }
                        )
