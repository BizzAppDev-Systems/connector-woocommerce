from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from odoo.addons.connector.exception import MappingError

# pylint: disable=W7950


class WooResCountryBatchImporter(Component):
    """Batch Importer for WooCommerce Country"""

    _name = "woo.res.country.batch.importer"
    _inherit = "woo.batch.importer"
    _apply_on = "woo.res.country"


class WooResCountryImportMapper(Component):
    """Impoter Mapper for the WooCommerce Country"""

    _name = "woo.res.country.import.mapper"
    _inherit = "woo.import.mapper"
    _apply_on = "woo.res.country"

    children = [
        ("states", "woo_state_line_ids", "woo.res.country.state"),
    ]

    @mapping
    def name(self, record):
        """Mapping for Name"""
        country_name = record.get("name")
        if not country_name:
            raise MappingError(_("Country Name not found!"))
        return {"name": country_name}

    @mapping
    def code(self, record):
        """Mapping for Code"""
        country_code = record.get("code")
        return {"code": country_code} if country_code else {}


class WooResCountryImporter(Component):
    """Importer the WooCommerce Country"""

    _name = "woo.res.country.importer"
    _inherit = "woo.importer"
    _apply_on = "woo.res.country"


class WooResCountryStateImportMapper(Component):
    _name = "woo.res.country.state.mapper"
    _inherit = "woo.import.mapper"
    _apply_on = "woo.res.country.state"

    direct = [
        ("id", "woo_state_id"),
        ("id", "external_id"),
        ("name", "name"),
    ]

    # def get_product(self, record):
    #     """Get The Binding of Product"""
    #     product_rec = record.get("product_id")
    #     if not product_rec:
    #         return False
    #     binder = self.binder_for("woo.product.product")
    #     product = binder.to_internal(product_rec, unwrap=True)
    #     return product

    # @mapping
    # def product_id(self, record):
    #     """Return Product excited in Woo order line and pre-check validations."""
    #     product_rec = record.get("product_id")
    #     if not product_rec:
    #         return {}
    #     product = self.get_product(record)
    #     return {"product_id": product.id, "product_uom": product.uom_id.id}

    # @mapping
    # def product_uom_qty(self, record):
    #     """Mapping for Product Uom qty"""
    #     product_qty = record.get("quantity")
    #     if not product_qty:
    #         product = self.get_product(record)
    #         error_message = (
    #             f"Order Line Product Quantity not found for Product: {product.name}"
    #         )
    #         raise MappingError(error_message)
    #     return {"product_uom_qty": product_qty}

    # @mapping
    # def price_unit(self, record):
    #     """Mapping for Price Unit"""
    #     unit_price = record.get("price")
    #     return {"price_unit": unit_price}

    # @mapping
    # def price_subtotal_line(self, record):
    #     """Mapping for Price Subtotal"""
    #     total = record.get("total")
    #     return {"price_subtotal_line": total} if total else {}

    # @mapping
    # def subtotal_line(self, record):
    #     """Mapping for Subtotal Line"""
    #     subtotal = record.get("subtotal")
    #     return {"subtotal_line": subtotal} if subtotal else {}

    # @mapping
    # def subtotal_tax_line(self, record):
    #     """Mapping for Subtotal Tax"""
    #     subtotal_tax = record.get("subtotal_tax")
    #     return {"subtotal_tax_line": subtotal_tax} if subtotal_tax else {}

    # @mapping
    # def total_tax_line(self, record):
    #     """Mapping for Total Tax Line"""
    #     total_tax = record.get("total_tax")
    #     return {"total_tax_line": total_tax} if total_tax else {}

    # @mapping
    # def name(self, record):
    #     """Mapping for Name"""
    #     name = record.get("name")
    #     if not name:
    #         raise MappingError(_("Order Line Name not found Please check!!!"))
    #     return {"name": name}

    # @mapping
    # def woo_order_id(self, record):
    #     """Mapping for Woo Order ID"""
    #     return {"woo_order_id": self.options.get("woo_order_id")}


class WooResCountryStateImporter(Component):
    _name = "woo.res.country.state.importer"
    _inherit = "woo.map.child.import"
    _apply_on = "woo.res.country.state"
