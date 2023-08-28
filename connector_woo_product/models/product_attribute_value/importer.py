import logging
from odoo import _
from odoo.addons.component.core import Component
from odoo.addons.connector.exception import MappingError
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
        """Mapping for name"""
        name = record.get("name")
        if not name:
            raise MappingError(_("Attribute Value Name is not found!"))
        return {"name": record.get("name")}

    @mapping
    def attribute_id(self, record):
        """Mapping for attribute_id"""
        attribute_id = record.get("attribute")
        binder = self.binder_for(model="woo.product.attribute")
        woo_attribute = binder.to_internal(attribute_id, unwrap=True)
        if not woo_attribute:
            raise MappingError(_("Attribute_id is not found!"))
        return {"attribute_id": woo_attribute.id}

    @mapping
    def description(self, record):
        """Mapping for description"""
        return (
            {"description": record.get("description")}
            if record.get("description")
            else {}
        )

    @only_create
    @mapping
    def update_product_attribute(self, record):
        """Update product attribute with imported attribute value."""
        attribute_id = record.get("attribute")
        attribute_value_name = record.get("name")
        binder = self.binder_for(model="woo.product.attribute")
        attribute = binder.to_internal(attribute_id, unwrap=True)
        if not attribute:
            return {}
        attribute_value = self.env["product.attribute.value"].search(
            [
                ("attribute_id", "=", attribute.id),
                ("name", "=", attribute_value_name),
            ],
            limit=1,
        )
        return {"value_ids": [(6, 0, attribute_value.ids)]} if attribute_value else {}