import logging

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create

_logger = logging.getLogger(__name__)


class WooProductAttributeValueBatchImporter(Component):
    """Batch Importer the WooCommerce Product Attribute Value"""

    _name = "woo.product.attribute.value.batch.importer"
    _inherit = "woo.batch.importer"
    _apply_on = "woo.product.attribute.value"


class WooAttributeValueImporter(Component):
    _name = "woo.product.attribute.value.importer"
    _inherit = "woo.importer"
    _apply_on = "woo.product.attribute.value"


class WooAttributeValueImportMapper(Component):
    _name = "woo.product.attribute.value.import.mapper"
    _inherit = "woo.import.mapper"
    _apply_on = ["woo.product.attribute.value"]

    @mapping
    def name(self, record):
        return {"name": record.get("name")}

    @mapping
    def attribute_id(self, record):
        # Assuming 'attribute' contains information about the WooCommerce attribute
        attribute_id = record.get("attribute")
        if attribute_id:
            attribute = self.env["woo.product.attribute"].search(
                [
                    ("external_id", "=", attribute_id),
                    ("backend_id", "=", self.backend_record.id),
                ],
                limit=1,
            )
            if attribute:
                return {"attribute_id": attribute.odoo_id.id}
            else:
                _logger.warning(
                    "WooCommerce attribute with ID %s not found in Odoo.",
                    attribute_id,
                )
        else:
            _logger.warning("No attribute ID found in the record.")
        return {}

    @mapping
    def description(self, record):
        return (
            {"description": record.get("description")}
            if record.get("description")
            else {}
        )

    @mapping
    def backend_id(self, record):
        """Return backend."""
        return {"backend_id": self.backend_record.id}

    @mapping
    def odoo_id(self, record):
        """Will bind the product to an existing one with the same code"""
        binder = self.binder_for(model="woo.product.attribute.value")
        woo_product = binder.to_internal(record.get("id"), unwrap=True)
        return {"odoo_id": woo_product.id} if woo_product else {}

    @only_create
    @mapping
    def update_product_attribute(self, record):
        """Update product attribute with imported attribute value."""
        attribute_id = record.get("attribute")
        attribute_value_name = record.get("name")
        attribute = self.env["woo.product.attribute"].search(
            [
                ("external_id", "=", attribute_id),
                ("backend_id", "=", self.backend_record.id),
            ],
            limit=1,
        )
        if attribute:
            attribute_value = self.env["product.attribute.value"].search(
                [
                    ("attribute_id", "=", attribute.id),
                    ("name", "=", attribute_value_name),
                ],
                limit=1,
            )
            if attribute_value:
                attribute.write({"value_ids": [(6, attribute_value.id)]})
            else:
                _logger.warning(
                    "Product attribute value with name %s not found for attribute %s in Odoo.",
                    attribute_value_name,
                    attribute.name,
                )
        else:
            _logger.warning("No attribute found for updating product attribute value.")
        return {}
