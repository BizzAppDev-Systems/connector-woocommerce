from odoo import models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    def make_bom(self, binding, env=None):
        """
        Create a Bill of Materials (BOM) for a product that is categorized
        as a 'Grouped' type in Woocommerce.

        This function checks if a BOM already exists for the product template in Odoo.
        If not, it creates a new BOM of 'phantom' type.

        If an existing BOM is found, It will check the components and if there is any
        changes found then it will archieve existing BoM and create the new BoM with
        Updated components.

        :param binding: The binding object of the product.
        """
        product_template = binding.odoo_id.product_tmpl_id

        existing_bom = self.search(
            [("product_tmpl_id", "=", product_template.id), ("active", "=", True)]
        )
        binder = env.binder_for("woo.product.product")

        product_records = {
            binder.to_internal(product, unwrap=True).id
            for product in env.remote_record.get("grouped_products", [])
        }

        if not existing_bom:
            self.create(
                {
                    "product_tmpl_id": product_template.id,
                    "type": "phantom",
                    "bom_line_ids": [
                        (0, 0, {"product_id": product_id})
                        for product_id in product_records
                    ],
                }
            )
        else:
            existing_product_ids = {
                line.product_id.id for line in existing_bom.bom_line_ids
            }
            products_to_add = product_records - existing_product_ids
            products_to_remove = existing_product_ids - product_records
            if products_to_add or products_to_remove:
                existing_bom.write({"active": False})
                self.create(
                    {
                        "product_tmpl_id": product_template.id,
                        "type": "phantom",
                        "bom_line_ids": [
                            (0, 0, {"product_id": product_id})
                            for product_id in product_records
                        ],
                    }
                )
