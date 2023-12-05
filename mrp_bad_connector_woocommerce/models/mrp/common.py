from odoo import models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    def make_bom(self, binding, env=None):
        """
        Create a Bill of Materials (BOM) for a product that is categorized
        as a 'Grouped' type in Woocommerce.
        """
        product_template = binding.odoo_id.product_tmpl_id
        existing_bom = self.search(
            [("product_tmpl_id", "=", product_template.id), ("active", "=", True)],
            limit=1,
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
            products_to_update = product_records.symmetric_difference(
                existing_product_ids
            )
            if products_to_update:
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
