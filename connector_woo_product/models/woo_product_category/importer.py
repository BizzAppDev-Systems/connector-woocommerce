import logging
from odoo import _
from odoo.addons.component.core import Component
from odoo.addons.connector.exception import MappingError
from odoo.addons.connector.components.mapper import mapping

# pylint: disable=W7950

_logger = logging.getLogger(__name__)


class WooProductCategoryBatchImporter(Component):
    """Batch Importer the WooCommerce Product"""

    _name = "woo.product.category.batch.importer"
    _inherit = "woo.batch.importer"
    _apply_on = "woo.product.category"


class WooProductCategoryImportMapper(Component):
    """Impoter Mapper for the WooCommerce Product Category"""

    _name = "woo.product.category.import.mapper"
    _inherit = "woo.import.mapper"
    _apply_on = "woo.product.category"

    @mapping
    def name(self, record):
        """Mapping for name"""
        name = record.get("name")
        if not name:
            raise MappingError(_("Category Name doesn't exist please check !!!"))
        return {"name": record.get("name")}

    @mapping
    def slug(self, record):
        """Mapping product slug"""
        slug = record.get("slug")
        return {"slug": slug} if slug else {}

    @mapping
    def display(self, record):
        """Mapped product default code."""
        display = record.get("display")
        return {"display": display} if display else {}

    @mapping
    def description(self, record):
        """Mapping for discription"""
        return {"description": record.get("description")}

    @mapping
    def menu_order(self, record):
        """Mapping for Menu Order"""
        return {"menu_order": record.get("menu_order")}

    @mapping
    def count(self, record):
        """Mapping for count"""
        return {"count": record.get("count")}

    @mapping
    def parent_id(self, record):
        """Mapping for Product Category"""
        binder = self.binder_for(model="woo.product.category")
        woo_parent = binder.to_internal(record.get("parent"), unwrap=True)
        return {"parent_id": woo_parent.id} if woo_parent else {}


class WooProductCategoryImporter(Component):
    """Importer the WooCommerce Product category"""

    _name = "woo.product.category.importer"
    _inherit = "woo.importer"
    _apply_on = "woo.product.category"
