import json
import logging

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping

_logger = logging.getLogger(__name__)


class WooProductExporterMapper(Component):
    _name = "woo.product.export.mapper"
    _inherit = "woo.product.common.export.mapper"
    _apply_on = "woo.product.product"
    _usage = "product.exporter.mapper"

    @mapping
    def name(self, record):
        """Mapping for name"""
        if record.product_template_variant_value_ids:
            return {}
        return {"name": record.name}

    @mapping
    def regular_price(self, record):
        """Mapping for regular_price"""
        return {"regular_price": str(record.lst_price) or ""}

    @mapping
    def product_template_variant_value_ids(self, record):
        """Mapping for attributes and name"""
        if not record.product_template_variant_value_ids:
            return {}
        attributes = []
        names = []
        for variant in record.product_template_variant_value_ids:
            attribute_and_value = {
                "id": variant.attribute_id.woo_bind_ids[0].external_id,
                "name": variant.attribute_id.name,
                "option": variant.product_attribute_value_id.name,
            }
            attributes.append(attribute_and_value)
            names.append(variant.product_attribute_value_id.name)
        combined_names = ", ".join(names)
        return {"attributes": attributes, "name": combined_names}


class WooProductExporter(Component):
    _name = "woo.product.exporter"
    _inherit = "woo.exporter"
    _apply_on = ["woo.product.product"]
    _usage = "product.exporter"
    _base_mapper_usage = "product.exporter.mapper"

    def _after_export(self):
        """Update the Woocommerce Product Binding values."""
        res = super(WooProductExporter, self)._after_export()
        category_ids = [
            category["id"] for category in self.response_data.get("categories", [])
        ]
        categories = self.env["woo.product.category"].search(
            [("external_id", "in", category_ids)]
        )
        self.binding.write(
            {
                "woo_data": json.dumps(self.response_data, indent=2),
                "woo_product_name": self.response_data.get("name"),
                "status": self.response_data.get("status"),
                "tax_status": self.response_data.get("tax_status"),
                "stock_status": self.response_data.get("stock_status"),
                "price": self.response_data.get("price"),
                "regular_price": self.response_data.get("regular_price"),
                "stock_management": self.response_data.get("manage_stock", False),
                "woo_product_categ_ids": [(6, 0, categories.ids)]
                if categories
                else False,
            }
        )
        return res
