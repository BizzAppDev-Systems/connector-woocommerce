import logging
from odoo.addons.component.core import Component
from odoo.addons.connector.exception import MappingError
from odoo import _
from odoo.addons.connector.components.mapper import mapping

# pylint: disable=W7950

_logger = logging.getLogger(__name__)


class WooProductProductBatchImporter(Component):
    """Batch Importer the WooCommerce Product"""

    _name = "woo.product.product.batch.importer"
    _inherit = "woo.batch.importer"
    _apply_on = "woo.product.product"


class WooProductProductImportMapper(Component):
    """Impoter Mapper for the WooCommerce Product"""

    _name = "woo.product.product.import.mapper"
    _inherit = "woo.import.mapper"
    _apply_on = "woo.product.product"

    @mapping
    def name(self, record):
        """Mapping for Name"""
        name = record.get("name")
        if not name:
            raise MappingError(_("Product name doesn't exist please check !!!"))
        return {"name": name}

    @mapping
    def list_price(self, record):
        """Mapping product Price"""
        return {"list_price": record.get("price")}

    @mapping
    def price(self, record):
        """Mapping for Standard Price"""
        price = record.get("price")
        return {"price": price} if price else {}

    @mapping
    def regular_price(self, record):
        """Mapping for Regular Price"""
        regular_price = record.get("regular_price")
        return {"regular_price": regular_price} if regular_price else {}

    @mapping
    def default_code(self, record):
        """Mapped product default code."""
        default_code = record.get("sku")
        if not default_code and not self.backend_record.without_sku:
            raise MappingError(_("SKU is Missing for the %s !", record.get("name")))
        return {"default_code": default_code} if default_code else {}

    @mapping
    def description(self, record):
        """Mapping for discription"""
        description = record.get("description")
        return {"description": description} if description else {}

    @mapping
    def purchase_ok(self, record):
        """Mapping for purchase_ok"""
        return {"purchase_ok": record.get("purchasable", False)}

    @mapping
    def status(self, record):
        """Mapping for status"""
        status = record.get("status")
        return {"status": status} if status else {}

    @mapping
    def tax_status(self, record):
        """Mapping for tax_status"""
        tax_status = record.get("tax_status")
        return {"tax_status": tax_status} if tax_status else {}

    @mapping
    def stock_status(self, record):
        """Mapping for stock_status"""
        stock_status = record.get("stock_status")
        return {"stock_status": stock_status} if stock_status else {}

    @mapping
    def categ_id(self, record):
        """Mapping for Odoo category"""
        product_category = self.backend_record.product_categ_id
        return {"categ_id": product_category.id} if product_category else {}

    def _get_product_attribute(self, attribute_id, record):
        """Get the product attribute"""
        binder = self.binder_for("woo.product.attribute")
        attribute_name = attribute_id.get("name")
        created_id = "{}-{}".format(attribute_name, record.get("id"))
        product_attribute = binder.to_internal(created_id)
        if not product_attribute and not attribute_id.get("id"):
            product_attribute = self.env["woo.product.attribute"].create(
                {
                    "name": attribute_name,
                    "backend_id": self.backend_record.id,
                    "external_id": created_id,
                }
            )
        return product_attribute

    def _create_attribute_values(self, options, product_attribute):
        """Create attribute value"""
        for option in options:
            product_attribute_value = self.env["product.attribute.value"].search(
                [
                    ("name", "=", option),
                    ("attribute_id", "=", product_attribute.odoo_id.id),
                ],
                limit=1,
            )
            if product_attribute_value:
                continue
            attribute_value = {
                "name": option,
                "attribute_id": product_attribute.odoo_id.id,
                "woo_attribute_id": product_attribute.id,
            }
            self.env["product.attribute.value"].create(attribute_value)
        return True

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
            product_attribute = self._get_product_attribute(attribute, record)
            if "options" in attribute:
                self._create_attribute_values(attribute["options"], product_attribute)
            attribute_ids.append(product_attribute.id)
        return {"woo_attribute_ids": [(6, 0, attribute_ids)]}

    @mapping
    def woo_product_categ_ids(self, record):
        """Mapping for woo_product_categ_ids"""
        category_ids = []
        woo_product_categories = record.get("categories", [])
        binder = self.binder_for("woo.product.category")
        for category in woo_product_categories:
            woo_binding = binder.to_internal(category.get("id"))
            if not woo_binding:
                continue
            category_ids.append(woo_binding.id)
        return {"woo_product_categ_ids": [(6, 0, category_ids)]} if category_ids else {}


class WooProductProductImporter(Component):
    """Importer the WooCommerce Product"""

    _name = "woo.product.product.importer"
    _inherit = "woo.importer"
    _apply_on = "woo.product.product"
