import logging

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping

# pylint: disable=W7950

_logger = logging.getLogger(__name__)


class WooProductCategoryBatchImporter(Component):
    """Batch Importer the WooCommerce Product"""

    _name = "woo.product.category.batch.importer"
    _inherit = "woo.batch.importer"
    _apply_on = "woocommerce.product.category"


class WooProductCategoryImportMapper(Component):
    """Impoter Mapper for the WooCommerce Product Category"""

    _name = "woo.product.category.import.mapper"
    _inherit = "woo.import.mapper"
    _apply_on = "woocommerce.product.category"

    @mapping
    def name(self, record):
        """Mapping for name"""
        product_name = record.get("name")
        return {"name": product_name}

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
        description = record.get("description")
        return {"description": description}

    @mapping
    def menu_order(self, record):
        """Mapping for sale_ok"""
        menu_order = record.get("menu_order")
        return {"menu_order": menu_order}

    @mapping
    def count(self, record):
        """Mapping for count"""
        count = record.get("count")
        return {"count": count}

    @mapping
    def parent_id(self, record):
        """Mapping for Product Category"""
        binder = self.binder_for(model="woocommerce.product.category")
        woo_parent = binder.to_internal(record.get("parent"), unwrap=True)
        return {"parent_id": woo_parent.id} if woo_parent else {}


class WooProductCategoryImporter(Component):
    """Importer the WooCommerce Product category"""

    _name = "woo.product.category.importer"
    _inherit = "woo.importer"
    _apply_on = "woocommerce.product.category"
