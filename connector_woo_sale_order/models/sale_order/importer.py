import logging
from odoo import _
from odoo.addons.component.core import Component
from odoo.addons.connector.exception import MappingError
from odoo.addons.connector.components.mapper import mapping
from odoo.addons.connector.components.mapper import mapping, only_create

# pylint: disable=W7950

_logger = logging.getLogger(__name__)


class WooSaleOrderBatchImporter(Component):
    _name = "woo.sale.order.batch.importer"
    _inherit = "woo.delayed.batch.importer"
    _apply_on = "woo.sale.order"


class WooSaleOrderImportMapper(Component):
    _name = "woo.sale.order.import.mapper"
    _inherit = "woo.import.mapper"
    _apply_on = "woo.sale.order"

    direct = [
        ("id", "external_id"),
        ("order_id", "woo_order_id"),
    ]

    children = [
        ("line_items", "woo_order_line_ids", "woo.sale.order.line"),
    ]

    @mapping
    def name(self, record):
        """Return name data with sale prefix."""
        name = record.get("order_key")
        if not name:
            raise MappingError(_("Sale Order Name not found Please check!!!"))
        if self.backend_record.order_prefix:
            name = "{}{}".format(self.backend_record.order_prefix, record.get("id"))
        return {"name": name}

    @only_create
    @mapping
    def partner_id(self, record):
        """Return the partner_id ."""
        binder = self.binder_for("woo.res.partner")
        if record.get("customer_id"):
            partner = binder.to_internal(record.get("customer_id"), unwrap=True)
            return {"partner_id": partner.id}
        else:
            billing = record.get("billing")
            shipping = record.get("shipping")
            partner_dict = (
                billing
                if billing.get("first_name") or billing.get("email")
                else shipping
            )
            partner_data = self.env["res.partner"]._prepare_child_partner_vals(
                partner_dict
            )
            partner = self.env["res.partner"].create(partner_data)
            data = partner.create_get_children(record, partner.id, self.backend_record)
            data_child = [(0, 0, child_added) for child_added in data]
            partner.write({"child_ids": data_child})
            return {"partner_id": partner.id}

    @mapping
    def discount_total(self, record):
        """Mapping for Discount Total"""
        return (
            {"discount_total": record.get("discount_total")}
            if record.get("discount_total")
            else {}
        )

    @mapping
    def discount_tax(self, record):
        """Mapping for Discount Tax"""
        return (
            {"discount_tax": record.get("discount_tax")}
            if record.get("discount_tax")
            else {}
        )

    @mapping
    def shipping_total(self, record):
        """Mapping for Shipping Total"""
        return (
            {"shipping_total": record.get("shipping_total")}
            if record.get("shipping_total")
            else {}
        )

    @mapping
    def shipping_tax(self, record):
        """Mapping for Shipping Tax"""
        return (
            {"shipping_tax": record.get("shipping_tax")}
            if record.get("shipping_tax")
            else {}
        )

    @mapping
    def cart_tax(self, record):
        """Mapping for Cart Tax"""
        return {"cart_tax": record.get("cart_tax")} if record.get("cart_tax") else {}

    @mapping
    def currency_id(self, record):
        """Mapping for Currency"""
        currency = self.env["res.currency"].search(
            [("name", "=", record.get("currency"))], limit=1
        )
        if not currency:
            return {}
        currency.write({"active": True})
        return {"currency_id": currency.id}

    @mapping
    def total_tax(self, record):
        """Mapping for Total Tax"""
        return {"total_tax": record.get("total_tax")} if record.get("total_tax") else {}

    @mapping
    def woo_amount_total(self, record):
        """Mapping for Amount Total"""
        return {"woo_amount_total": record.get("total")} if record.get("total") else {}

    @mapping
    def amount_tax(self, record):
        """Mapping for Amount Tax"""
        return (
            {"amount_tax": record.get("total_tax")} if record.get("total_tax") else {}
        )

    @mapping
    def update_order_id(self, record):
        """Update the order_id"""
        self.options.update(order_id=record.get("id"))


class WooSaleOrderImporter(Component):
    _name = "woo.sale.order.importer"
    _inherit = "woo.importer"
    _apply_on = "woo.sale.order"

    def _must_skip(self):
        """Skipped Record which are already imported."""
        if self.binder.to_internal(self.external_id):
            return _("Already imported")
        return super(WooSaleOrderImporter, self)._must_skip()

    def _import_dependencies(self):
        record = self.remote_record
        for line in record.get("items", []):
            _logger.debug("line: %s", line)
            if "product_id" in line:
                self._import_dependency(line["id"], "woo.product.product")


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
    def product_id(self, record):
        """Return Product excited in Woo order line and pre-check validations."""
        if not record.get("product_id"):
            return {}
        binder = self.binder_for("woo.product.product")
        product = binder.to_internal(record.get("product_id"), unwrap=True)
        return {"product_id": product.id}

    @mapping
    def product_uom_qty(self, record):
        """Mapping for Product Uom qty"""
        product_qty = record.get("quantity")
        if not product_qty:
            raise MappingError(
                _("Order Line Product Quantity not found Please check!!!")
            )
        return {"product_uom_qty": record.get("quantity")}

    @mapping
    def price_unit(self, record):
        """Mapping for Price Unit"""
        unit_price = record.get("price")
        if not unit_price:
            raise MappingError(_("Order Line Price Unit not found Please check!!!"))
        return {"price_unit": unit_price}

    @mapping
    def tax_id(self, record):
        """Mapping for Tax"""
        if not record.get("taxes"):
            return {}

    @mapping
    def price_subtotal(self, record):
        """Mapping for Price Subtotal"""
        return {"price_subtotal": record.get("total")}

    @mapping
    def name(self, record):
        """Mapping for Name"""
        name = record.get("name")
        if not name:
            raise MappingError(_("Order Line Name not found Please check!!!"))
        return {"name": name}

    @mapping
    def order_id(self, record):
        """Mapping for Order"""
        order_id = self.options.get("order_id")
        if not order_id:
            raise MappingError(_("Order Line Order Id not found Please check!!!"))
        return {"order_id": order_id}


class WooSaleOrderLineImporter(Component):
    _name = "woo.sale.order.line.importer"
    _inherit = "woo.map.child.import"
    _apply_on = "woo.sale.order.line"
