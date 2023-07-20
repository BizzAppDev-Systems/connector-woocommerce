import logging

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create

# pylint: disable=W7950

_logger = logging.getLogger(__name__)


class WooProductProductBatchImporter(Component):
    """Batch Importer the WooCommerce Product"""

    _name = "woo.product.product.batch.importer"
    _inherit = "woo.delayed.batch.importer"
    _apply_on = "woo.product.product"


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
        """Will bind the partner to an existing one with the same code"""
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
    def default_code(self, record):
        """Mapped product default code."""
        default_code = record.get("sku")
        if not default_code:
            return {}
        return {"default_code": default_code}

    @mapping
    def description(self, record):
        """Mapping for discription"""
        description = record.get("description")
        return {"description": description}

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
    def backend_id(self, record):
        """Return backend."""
        return {"backend_id": self.backend_record.id}


class WooProductProductImporter(Component):
    """Importer the WooCommerce Product"""

    _name = "woo.product.product.importer"
    _inherit = "woo.importer"
    _apply_on = "woo.product.product"
