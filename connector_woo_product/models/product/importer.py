import logging

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from odoo.addons.connector.exception import MappingError

# pylint: disable=W7950

_logger = logging.getLogger(__name__)


class WooProductProductBatchImporter(Component):
    """Batch Importer the WooCommerce Product"""

    _name = "woo.product.product.batch.importer"
    _inherit = "woo.batch.importer"
    _apply_on = "woo.product.product"

    def run(self, filters=None, force=None):
        """Run the synchronization"""
        filters = filters or {}
        try:
            records = self.backend_adapter.search(filters)
            for record in records:
                external_id = record.get(self.backend_adapter._woo_ext_id_key)
                self._import_record(external_id, data=record)
        except Exception as err:
            raise ValidationError(_("Error : %s") % err) from err


class WooProductProductImportMapper(Component):
    """Impoter Mapper for the WooCommerce Product"""

    _name = "woo.product.product.import.mapper"
    _inherit = "woo.import.mapper"
    _apply_on = "woo.product.product"

    @mapping
    def name(self, record):
        """Mapping for name"""
        name = record.get("name")
        if not name:
            raise MappingError(_("Attribute Name is not found!"))
        return {"name": name}

    @mapping
    def list_price(self, record):
        """Mapping product price"""
        return {"list_price": record.get("price")}

    @mapping
    def standard_price(self, record):
        """Mapping for standard_price"""
        return {"standard_price": record.get("regular_price")}

    @mapping
    def default_code(self, record):
        """Mapped product default code."""
        default_code = record.get("sku")
        return {"default_code": default_code} if default_code else {}

    @mapping
    def description(self, record):
        """Mapping for discription"""
        description = record.get("description")
        return {"description": description} if description else {}

    @mapping
    def sale_ok(self, record):
        """Mapping for sale_ok"""
        return {"sale_ok": record.get("on_sale", False)}

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

    def _get_product_attribute(self, attribute_id, record):
        """Get the product attribute"""
        binder = self.binder_for("woo.product.attribute")
        attribute_name = attribute_id.get("name")
        created_id = "{}-{}".format(attribute_name, record.get("id"))
        product_attribute = binder.to_internal(created_id)
        if not product_attribute:
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
        woo_product_attribute = record.get("attributes")
        if not woo_product_attribute:
            return {}
        binder = self.binder_for("woo.product.attribute")
        for attribute_id in woo_product_attribute:
            attribute = attribute_id.get("id")
            woo_binding = binder.to_internal(attribute)
            if woo_binding:
                attribute_ids.append(woo_binding.id)
                continue
            product_attribute = self._get_product_attribute(attribute_id, record)
            if "options" in attribute_id:
                self._create_attribute_values(
                    attribute_id["options"], product_attribute
                )

            attribute_ids.append(product_attribute.id)
        return {"woo_attribute_ids": [(6, 0, attribute_ids)]}

    @mapping
    def woo_product_categ_ids(self, record):
        """Mapping for woo_product_categ_ids"""
        category_ids = []
        woo_product_category = record.get("categories")
        binder = self.binder_for("woocommerce.product.category")
        for category in woo_product_category:
            woo_binding = binder.to_internal(category.get("id"))
            if woo_binding:
                category_ids.append(woo_binding.id)
                continue
            values = {
                "name": category.get("name"),
                "parent_id": category.get("parent"),
                "backend_id": self.backend_record.id,
                "external_id": category.get("id"),
            }
            category_ids.append([(0, 0, values)])
        return {"woo_product_categ_ids": [(6, 0, category_ids)]} if category_ids else {}


class WooProductProductImporter(Component):
    """Importer the WooCommerce Product"""

    _name = "woo.product.product.importer"
    _inherit = "woo.importer"
    _apply_on = "woo.product.product"
