from odoo import models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    def make_bom(self, binding, env=None):
        """
        Create a Bill of Materials (BOM) for a product that is categorized
        as a 'Grouped' type in Woocommerce.

        This function checks if a BOM already exists for the product template in Odoo.
        If not, it creates a new BOM of 'phantom' type.

        If an existing BOM is found, it updates the BOM by adding
        new products in components that are not already included.

        :param binding: The binding object of the product.
        """
        product_template = binding.odoo_id.product_tmpl_id

        existing_bom = self.search([("product_tmpl_id", "=", product_template.id)])
        binder = env.binder_for("woo.product.product")

        product_records = [
            (0, 0, {"product_id": binder.to_internal(product, unwrap=True).id})
            for product in env.remote_record.get("grouped_products", [])
        ]

        if not existing_bom:
            self.create(
                {
                    "product_tmpl_id": product_template.id,
                    "type": "phantom",
                    "bom_line_ids": product_records,
                }
            )
        else:
            existing_product_ids = existing_bom.bom_line_ids.mapped("product_id.id")
            new_product_records = [
                record
                for record in product_records
                if record[2]["product_id"] not in existing_product_ids
            ]
            if new_product_records:
                existing_bom.write({"bom_line_ids": new_product_records})
