import logging

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create

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

    @only_create
    @mapping
    def odoo_id(self, record):
        """Will bind the Product to an existing one with the same code"""
        binder = self.binder_for(model="woocommerce.product.category")
        woo_product = binder.to_internal(record.get("id"), unwrap=True)
        if woo_product:
            return {"odoo_id": woo_product.id}
        return {}

    @mapping
    def slug(self, record):
        """Mapping product slug"""
        slug = record.get("slug")
        return {"slug": slug}

    @mapping
    def display(self, record):
        """Mapped product default code."""
        display = record.get("display")
        if not display:
            return {}
        return {"display": display}

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
        """Mapping for Parent"""
        binder = self.binder_for(model="woocommerce.product.category")
        woo_parent = binder.to_internal(record.get("parent"), unwrap=True)
        if woo_parent:
            return {"parent_id": woo_parent.id}
        return {}

    @mapping
    def backend_id(self, record):
        """Return backend."""
        return {"backend_id": self.backend_record.id}


class WooProductCategoryImporter(Component):
    """Importer the WooCommerce Product category"""

    _name = "woo.product.category.importer"
    _inherit = "woo.importer"
    _apply_on = "woocommerce.product.category"
