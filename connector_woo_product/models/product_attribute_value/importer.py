import logging
from odoo import _
from odoo.addons.component.core import Component
from odoo.addons.connector.exception import MappingError
from odoo.addons.connector.components.mapper import mapping

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
            raise MappingError(_("Attribute Value Name doesn't exist please check !!!"))
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
