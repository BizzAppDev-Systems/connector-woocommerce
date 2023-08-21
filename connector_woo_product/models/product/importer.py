import logging
import base64
import requests
from odoo.addons.component.core import Component
from odoo.exceptions import ValidationError
from odoo import _
from odoo.addons.connector.components.mapper import mapping, only_create

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
            records = self.backend_adapter.search_read(filters)
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
        product_name = record.get("name")
        return {"name": product_name}

    @only_create
    @mapping
    def odoo_id(self, record):
        """Will bind the product to an existing one with the same code"""
        binder = self.binder_for(model="woo.product.product")
        woo_product = binder.to_internal(record.get("id"), unwrap=True)
        if woo_product:
            return {"odoo_id": woo_product.id}
        return {}

    @mapping
    def list_price(self, record):
        """Mapping product price"""
        price = record.get("price")
        return {"list_price": price}

    @mapping
    def standard_price(self, record):
        """Mapping for standard_price"""
        regular_price = record.get("regular_price")
        return {"standard_price": regular_price}

    @mapping
    def default_code(self, record):
        """Mapped product default code."""
        default_code = record.get("sku")
        if default_code:
            return {"default_code": default_code}
        return {}

    @mapping
    def description(self, record):
        """Mapping for discription"""
        description = record.get("description")
        return {"description": description}

    @mapping
    def image_1920(self, record):
        """Mapping of image"""
        image = record.get("images")
        if not image:
            return {}
        for img in image:
            image_src = img.get("src")
            response = requests.get(image_src)
            binary_data = response.content
            base64_data = base64.b64encode(binary_data).decode("utf-8")
        return {"image_1920": base64_data}

    @mapping
    def sale_ok(self, record):
        """Mapping for sale_ok"""
        sale = record.get("on_sale", False)
        return {"sale_ok": sale}

    @mapping
    def purchase_ok(self, record):
        """Mapping for purchase_ok"""
        purchase = record.get("purchasable", False)
        return {"purchase_ok": purchase}

    @mapping
    def status(self, record):
        """Mapping for status"""
        status = record.get("status")
        return {"status": status}

    @mapping
    def tax_status(self, record):
        """Mapping for tax_status"""
        tax_status = record.get("tax_status")
        return {"tax_status": tax_status}

    @mapping
    def stock_status(self, record):
        """Mapping for stock_status"""
        stock_status = record.get("stock_status")
        return {"stock_status": stock_status}

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
            else:
                created_id = "{}-{}".format(attribute_id.get("name"), record.get("id"))
                product_attribute = self.env["woo.product.attribute"].search(
                    [
                        ("name", "=", attribute_id.get("name")),
                        ("backend_id", "=", self.backend_record.id),
                        ("external_id", "=", created_id),
                    ],
                    limit=1,
                )
                if not product_attribute:
                    product_attribute = self.env["woo.product.attribute"].create(
                        {
                            "name": attribute_id.get("name"),
                            "backend_id": self.backend_record.id,
                            "external_id": created_id,
                        }
                    )
                if "options" in attribute_id:
                    for option in attribute_id.get("options"):
                        product_attribute_value = self.env[
                            "product.attribute.value"
                        ].search(
                            [
                                ("name", "=", option),
                                ("attribute_id", "=", product_attribute.odoo_id.id),
                            ],
                            limit=1,
                        )
                        if not product_attribute_value:
                            value = self.env["product.attribute.value"].create(
                                {
                                    "name": option,
                                    "attribute_id": product_attribute.odoo_id.id,
                                    "woo_attribute_id": product_attribute.id,
                                }
                            )
                attribute_ids.append(product_attribute.id)
        return {"woo_attribute_ids": attribute_ids}

    @mapping
    def woo_product_categ_ids(self, record):
        """Mapping for woo_product_categ_ids"""
        category_ids = []
        woo_product_category = record.get("categories")
        binder = self.binder_for("woocommerce.product.category")
        for category_id in woo_product_category:
            woo_binding = binder.to_internal(category_id.get("id"))
            if woo_binding:
                category_ids.append(woo_binding.id)
            else:
                product_category = self.env["woocommerce.product.category"].create(
                    {
                        "name": category_id.get("name"),
                        "parent_id": category_id.get("parent"),
                        "backend_id": self.backend_record.id,
                        "external_id": category_id.get("id"),
                    }
                )
                category_ids.append(product_category.id)
        return {"woo_product_categ_ids": category_ids}

    @mapping
    def backend_id(self, record):
        """Return backend."""
        return {"backend_id": self.backend_record.id}


class WooProductProductImporter(Component):
    """Importer the WooCommerce Product"""

    _name = "woo.product.product.importer"
    _inherit = "woo.importer"
    _apply_on = "woo.product.product"
