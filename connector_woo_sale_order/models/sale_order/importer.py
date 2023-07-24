import logging

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from odoo.addons.connector.exception import MappingError

# pylint: disable=W7950
# from odoo.addons.connector_shopify.components.misc import date_parser

_logger = logging.getLogger(__name__)


class WooSaleOrderBatchImporter(Component):
    _name = "woo.sale.order.batch.importer"
    _inherit = "woo.delayed.batch.importer"
    _apply_on = "woo.sale.order"


class WooSaleOrderImportMapper(Component):
    _name = "woo.sale.order.import.mapper"
    _inherit = "woo.import.mapper"
    _apply_on = "woo.sale.order"

    direct = [("id", "id")]

    children = [
        ("line_items", "woo_order_line_ids", "woo.sale.order.line"),
    ]

    @mapping
    def name(self, record):
        """Return name data with sale prefix."""
        name = record.get("order_key")
        return {"name": name}

    @mapping
    def partner_id(self, record):
        """Return the partner_id ."""
        binder = self.binder_for("woo.res.partner")
        partner = binder.to_internal(record.get("customer_id"), unwrap=True)
        if not partner:
            return {}
        return {"partner_id": partner.id}

    @mapping
    def order_line(self, record):
        items = record.get("line_items")
        order_line = []
        for item in items:
            vals = {
                "product_uom_qty": item.get("quantity"),
                "product_id": record.get("product_id"),
                "price_unit": 0,
            }
            order_line.append((0, 0, vals))
        return {"order_line": order_line}

    @mapping
    def currency_id(self, record):
        return {"currency_id": record.get("currency")}

    @mapping
    def amount_total(self, record):
        return {"amount_total": record.get("total")}

    @mapping
    def amount_tax(self, record):
        return {"amount_tax": record.get("total_tax")}

    @mapping
    def external_id(self, record):
        """Return external id."""
        return {"external_id": record.get("id")}

    @mapping
    def backend_id(self, record):
        """Return backend."""
        return {"backend_id": self.backend_record.id}


class WooSaleOrderImporter(Component):
    _name = "woo.sale.order.importer"
    _inherit = "woo.importer"
    _apply_on = "woo.sale.order"


# Sale Order Line


class WooSaleOrderLineImportMapper(Component):
    _name = "woo.sale.order.line.mapper"
    _inherit = "woo.import.mapper"
    _apply_on = "woo.sale.order.line"

    direct = [
        ("id", "woo_line_id"),
        ("id", "external_id"),
        ("name", "name"),
    ]

    @mapping
    def odoo_id(self, record):
        """Return sale order line."""
        line = self.env["sale.order.line"].search(
            [("woo_line_id", "=", record["id"])], limit=1
        )
        if not line:
            return {}
        return {"odoo_id": line.id}

    @mapping
    def product_id(self, record):
        """Return Product excited in Woo order line and pre-check validations."""
        print("hellllllllllooooooooooooo worrrrrrrrrrrrkkkkkkkkkkkiiiiiiiingggg")
        print(record, "lllllllllllllllllllllllllllllllllll")
        binder = self.binder_for("woo.product.product")
        product = binder.to_internal(record.get("product_id"), unwrap=True)
        if not product:
            return {}
        # product_id = record.get("line_items").get("product_id")
        # product = binder.to_internal(product_id, unwrap=True)
        return {"product_id": product.id}

    # @mapping
    # def name(self, record):
    #     print({"name": record.get("name")},"lllllllllllllllllll")
    #     return {"name": record.get("name")}

    @mapping
    def order_id(self, record):
        return {"order_id": record.get("id")}


class WooSaleOrderLineImporter(Component):
    _name = "woo.sale.order.line.importer"
    _inherit = "woo.map.child.import"
    _apply_on = "woo.sale.order.line"
