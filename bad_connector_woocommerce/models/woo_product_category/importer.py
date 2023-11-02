import logging

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create
from odoo.addons.connector.exception import MappingError

# pylint: disable=W7950

_logger = logging.getLogger(__name__)


class WooProductCategoryBatchImporter(Component):
    """Batch Importer the WooCommerce Product"""

    _name = "woo.product.category.batch.importer"
    _inherit = "woo.delayed.batch.importer"
    _apply_on = "woo.product.category"


class WooProductCategoryImportMapper(Component):
    """Impoter Mapper for the WooCommerce Product Category"""

    _name = "woo.product.category.import.mapper"
    _inherit = "woo.import.mapper"
    _apply_on = "woo.product.category"

    @only_create
    @mapping
    def odoo_id(self, record):
        """Creating odoo id"""
        if "data" in record:
            record=record.get("data")
        category_name = record.get("name")
        product_category = self.env["product.category"].search(
            [("name", "=", category_name)], limit=1
        )
        return {"odoo_id": product_category.id} if product_category else {}

    @mapping
    def name(self, record):
        """Mapping for Name"""
        if "data" in record:
            record=record.get("data")
        name = record.get("name")
        if not name:
            raise MappingError(_("Category Name doesn't exist please check !!!"))
        return {"name": record.get("name")}

    @mapping
    def slug(self, record):
        """Mapping product Slug"""
        if "data" in record:
            record=record.get("data")
        slug = record.get("slug")
        return {"slug": slug} if slug else {}

    @mapping
    def display(self, record):
        """Mapped for Display."""
        if "data" in record:
            record=record.get("data")
        display = record.get("display")
        return {"display": display} if display else {}

    @mapping
    def description(self, record):
        """Mapping for Description"""
        if "data" in record:
            record=record.get("data")
        return {"description": record.get("description")}

    @mapping
    def menu_order(self, record):
        """Mapping for Menu Order"""
        if "data" in record:
            record=record.get("data")
        return {"menu_order": record.get("menu_order")}

    @mapping
    def count(self, record):
        """Mapping for Count"""
        if "data" in record:
            record=record.get("data")
        return {"count": record.get("count")}

    @mapping
    def parent_id(self, record):
        """Mapping for Parent Product Category"""
        if "data" in record:
            record=record.get("data")
        binder = self.binder_for(model="woo.product.category")
        woo_parent = binder.to_internal(record.get("parent"), unwrap=True)
        return {"parent_id": woo_parent.id} if woo_parent else {}


class WooProductCategoryImporter(Component):
    """Importer the WooCommerce Product category"""

    _name = "woo.product.category.importer"
    _inherit = "woo.importer"
    _apply_on = "woo.product.category"
