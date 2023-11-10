import logging

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from odoo.addons.connector.exception import MappingError

# pylint: disable=W7950

_logger = logging.getLogger(__name__)


class WooProductTemplateBatchImporter(Component):
    """Batch Importer the WooCommerce Product Template"""

    _name = "woo.product.template.batch.importer"
    _inherit = "woo.delayed.batch.importer"
    _apply_on = "woo.product.template"


class WooProductTemplateImportMapper(Component):
    """Impoter Mapper for the WooCommerce Product Template"""

    _name = "woo.product.template.import.mapper"
    _inherit = "woo.import.mapper"
    _apply_on = "woo.product.template"

    @mapping
    def name(self, record):
        """Mapping for Name"""
        name = record.get("name")
        product_tmp_id = record.get("id")
        if not name:
            raise MappingError(
                _("Product Template name doesn't exist for Product ID %s Please check")
                % product_tmp_id
            )
        return {"name": name}

    def _get_attribute_id_format(self, attribute, record, option=None):
        """Return the attribute and attribute value's unique id"""
        if not option:
            return "{}-{}".format(attribute.get("name"), record.get("id"))
        return "{}-{}-{}".format(option, attribute.get("id"), record.get("id"))

    @mapping
    def woo_attribute_ids(self, record):
        """Mapping of woo_attribute_ids"""
        attribute_ids = []
        woo_product_attributes = record.get("attributes", [])
        if not woo_product_attributes:
            return {}
        binder = self.binder_for("woo.product.attribute")
        for attribute in woo_product_attributes:
            attribute_id = attribute.get("id")
            woo_binding = binder.to_internal(attribute_id)
            if woo_binding:
                attribute_ids.append(woo_binding.id)
                continue
            product = self.env["product.product"]
            product_attribute = product._get_product_attribute(
                attribute, record, env=self
            )
            if "options" in attribute:
                product._create_attribute_values(
                    attribute["options"], product_attribute, attribute, record, env=self
                )
            attribute_ids.append(product_attribute.id)
        return {"woo_attribute_ids": [(6, 0, attribute_ids)]}

    @mapping
    def woo_product_attribute_value_ids(self, record):
        """Mapping for woo_product_attribute_value_ids"""
        attribute_value_ids = []
        woo_attributes = record.get("attributes", [])
        binder = self.binder_for("woo.product.attribute")
        for woo_attribute in woo_attributes:
            attribute_id = woo_attribute.get("id")
            if attribute_id == 0:
                attribute_id = self._get_attribute_id_format(woo_attribute, record)
            attribute = binder.to_internal(attribute_id, unwrap=True)
            options = woo_attribute.get("options", [])
            for option in options:
                attribute_value = self.env["woo.product.attribute.value"].search(
                    [
                        ("name", "=", option),
                        ("attribute_id", "=", attribute.id),
                    ],
                    limit=1,
                )
                if not attribute_value:
                    raise MappingError(
                        _("'%s' attribute value not found!Import Attribute first.")
                        % option
                    )
                attribute_value_ids.append(attribute_value.id)
        return {"woo_product_attribute_value_ids": [(6, 0, attribute_value_ids)]}

    @mapping
    def variant_different(self, record):
        attributes = record.get("attributes", [])
        variation_count_from_payload = 1
        for attribute in attributes:
            if attribute.get("variation"):
                options = attribute.get("options")
                if options:
                    variation_count_from_payload *= len(options)
        if variation_count_from_payload == len(record.get("variations", [])):
            return {"variant_different": False}
        else:
            return {"variant_different": True}

    def _prepare_attribute_line(self, attribute, value_ids):
        """Prepare an attribute line."""
        attribute_line = {
            "attribute_id": attribute.id,
            "value_ids": [(6, 0, value_ids)],
        }
        return attribute_line

    def _get_attribute_lines(self, map_record):
        """Get all attribute lines for the product."""
        attribute_lines = []
        attribute_binder = self.binder_for("woo.product.attribute")
        template_binder = self.binder_for("woo.product.template")

        record = map_record.source

        for woo_attribute in record.get("attributes", []):
            woo_attribute_id = woo_attribute.get("id", 0)
            woo_attribute_id = (
                self._get_attribute_id_format(woo_attribute, record)
                if woo_attribute_id == 0
                else woo_attribute_id
            )

            attribute = attribute_binder.to_internal(woo_attribute_id, unwrap=True)
            product_template = template_binder.to_internal(
                record.get("id"), unwrap=True
            )

            # Check if the attribute line already exists for the product_template.
            existing_attribute_line = product_template.attribute_line_ids.filtered(
                lambda line: line.attribute_id.id == attribute.id
            )

            value_ids = [
                value.id
                for option in woo_attribute.get("options", [])
                for value in attribute.value_ids.filtered(lambda v: v.name == option)
            ]

            # If the attribute line already exists, update it.
            if existing_attribute_line:
                existing_attribute_line.write({"value_ids": [(6, 0, value_ids)]})
            # Otherwise, create a new attribute line.
            else:
                attribute_line = self._prepare_attribute_line(attribute, value_ids)
                attribute_lines.append((0, 0, attribute_line))

        return attribute_lines

    def finalize(self, map_record, values):
        """Override the finalize method to add attribute lines to the product."""
        attribute_lines = self._get_attribute_lines(map_record)
        values.update({"attribute_line_ids": attribute_lines})
        return super(WooProductTemplateImportMapper, self).finalize(map_record, values)


class WooProductTemplateImporter(Component):
    """Importer the WooCommerce Product Template"""

    _name = "woo.product.template.importer"
    _inherit = "woo.importer"
    _apply_on = "woo.product.template"
