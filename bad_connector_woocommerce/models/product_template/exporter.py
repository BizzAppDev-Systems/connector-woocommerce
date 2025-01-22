import json
import logging

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from odoo.addons.connector.exception import MappingError

_logger = logging.getLogger(__name__)


class WooProductTemplateExporterMapper(Component):
    _name = "woo.product.template.export.mapper"
    _inherit = "woo.product.common.export.mapper"
    _apply_on = "woo.product.template"

    @mapping
    def name(self, record):
        """Mapping for name"""
        return {"name": record.name}

    @mapping
    def type(self, record):
        """Mapping for Type"""
        return {"type": "variable"}

    @mapping
    def regular_price(self, record):
        """Mapping for regular_price"""
        return {"regular_price": str(record.list_price) or ""}

    @mapping
    def attributes(self, record):
        """Mapping for attributes (color, size, etc.)"""
        attributes = []
        for attribute in record.attribute_line_ids:
            if not attribute.attribute_id.woo_bind_ids:
                raise MappingError(
                    _(
                        "Selected attribute '%s' is not present in WooCommerce",
                        attribute.attribute_id.name,
                    )
                )
            woo_attribute = attribute.attribute_id.woo_bind_ids[0].external_id
            woo_attribute_name = attribute.attribute_id.name
            options = []
            for value in attribute.value_ids:
                if not value.woo_bind_ids:
                    raise MappingError(
                        _(
                            "Selected attribute value '%s' is not present in "
                            "WooCommerce",
                            attribute.value.name,
                        )
                    )
                woo_value_name = value.name
                options.append(woo_value_name)
            attributes.append(
                {
                    "id": woo_attribute,
                    "name": woo_attribute_name,
                    "visible": True,
                    "variation": True,
                    "options": options,
                }
            )

        return {"attributes": attributes}


class WooProductTemplateExporter(Component):
    _name = "woo.product.template.exporter"
    _inherit = "woo.exporter"
    _apply_on = ["woo.product.template"]

    def _after_export(self):
        """Update the Woocommerce Product Binding values and Export its variants."""
        res = super(WooProductTemplateExporter, self)._after_export()
        category_ids = [
            category["id"] for category in self.response_data.get("categories", [])
        ]
        categories = self.env["woo.product.category"].search(
            [("external_id", "in", category_ids)]
        )
        self.binding.write(
            {
                "woo_data": json.dumps(self.response_data, indent=2),
                "woo_product_categ_ids": [(6, 0, categories.ids)] if categories else [],
            }
        )
        if not self.binding.odoo_id.product_variant_ids:
            return res
        for product in self.binding.odoo_id.product_variant_ids:
            kwargs = {}
            kwargs["product_external_id"] = self.response_data.get("id")
            model = self.env["woo.product.product"]
            job_options = {}
            description = self.backend_record.get_queue_job_description(
                prefix=model.export_product.__doc__ or "Record Export To",
                model=model._description,
            )
            job_options["description"] = description
            delayable = model.with_delay(**job_options or {})
            delayable.export_product(
                backend=self.backend_record, record=product, **kwargs
            )
        return res
