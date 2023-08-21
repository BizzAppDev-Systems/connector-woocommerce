import logging
from odoo import _
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create
from odoo.exceptions import ValidationError

# pylint: disable=W7950

_logger = logging.getLogger(__name__)


class WooProductAttributeBatchImporter(Component):
    """Batch Importer the WooCommerce Product Attribute"""

    _name = "woo.product.attribute.batch.importer"
    _inherit = "woo.batch.importer"
    _apply_on = "woo.product.attribute"

    def run(self, filters=None, force=None):
        """Run the synchronization"""
        filters = filters or {}
        try:
            records = self.backend_adapter.search_read(filters)
            for record in records:
                external_id = record.get(self.backend_adapter._woo_ext_id_key)
                self._import_record(external_id, data=record)
        except Exception as err:
            raise ValidationError(_("Error : %s") % err) from err


class WooProductAttributeImportMapper(Component):
    """Impoter Mapper for the WooCommerce Product Attribute"""

    _name = "woo.product.attribute.import.mapper"
    _inherit = "woo.import.mapper"
    _apply_on = "woo.product.attribute"

    @mapping
    def name(self, record):
        """Mapping for name"""
        product_attribute_name = record.get("name")
        return {"name": product_attribute_name}

    @mapping
    def odoo_id(self, record):
        """Will bind the partner to an existing one with the same code"""
        binder = self.binder_for(model="woo.product.attribute")
        woo_product_attribute = binder.to_internal(record.get("id"), unwrap=True)
        if woo_product_attribute:
            return {"odoo_id": woo_product_attribute.id}
        return {}

    @mapping
    def has_archives(self, record):
        """Mapping product has_archives"""
        has_archives = record.get("has_archives")
        return {"has_archives": has_archives}

    @mapping
    def backend_id(self, record):
        """Return backend."""
        return {"backend_id": self.backend_record.id}


class WooProductAttributeImporter(Component):
    """Importer the WooCommerce Product"""

    _name = "woo.product.attribute.importer"
    _inherit = "woo.importer"
    _apply_on = ["woo.product.attribute"]
