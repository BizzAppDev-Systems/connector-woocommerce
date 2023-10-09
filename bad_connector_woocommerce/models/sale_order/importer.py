import logging

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create
from odoo.addons.connector.exception import MappingError

# pylint: disable=W7950

_logger = logging.getLogger(__name__)


class WooSaleOrderBatchImporter(Component):
    _name = "woo.sale.order.batch.importer"
    _inherit = "woo.batch.importer"
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
        discount_total = record.get("discount_total")
        return {"discount_total": discount_total} if discount_total else {}

    @mapping
    def discount_tax(self, record):
        """Mapping for Discount Tax"""
        discount_tax = record.get("discount_tax")
        return {"discount_tax": discount_tax} if discount_tax else {}

    @mapping
    def shipping_total(self, record):
        """Mapping for Shipping Total"""
        shipping_total = record.get("shipping_total")
        return {"shipping_total": shipping_total} if shipping_total else {}

    @mapping
    def shipping_tax(self, record):
        """Mapping for Shipping Tax"""
        shipping_tax = record.get("shipping_tax")
        return {"shipping_tax": shipping_tax} if shipping_tax else {}

    @mapping
    def cart_tax(self, record):
        """Mapping for Cart Tax"""
        cart_tax = record.get("cart_tax")
        return {"cart_tax": cart_tax} if cart_tax else {}

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
        total_tax = record.get("total_tax")
        return {"total_tax": total_tax} if total_tax else {}

    @mapping
    def woo_amount_total(self, record):
        """Mapping for Amount Total"""
        total = record.get("total")
        return {"woo_amount_total": total} if total else {}

    @mapping
    def amount_tax(self, record):
        """Mapping for Amount Tax"""
        total_tax = record.get("total_tax")
        return {"amount_tax": total_tax} if total_tax else {}

    @mapping
    def woo_order_status(self, record):
        """Mapping for Order Status"""
        status = record.get("status")
        return {"woo_order_status": status} if status else {}

    @mapping
    def update_woo_order_id(self, record):
        """Update the woo_order_id"""
        woo_order_id = record.get("id")
        if not woo_order_id:
            raise MappingError(_("WooCommerce Order ID not found Please check!!!"))
        self.options.update(woo_order_id=woo_order_id)
        return {"woo_order_id": woo_order_id}

    @mapping
    def woo_coupon(self, record):
        """Mapping for woo_coupon"""
        woo_coupons = record.get("coupon_lines", [])
        if not woo_coupons:
            return {}
        coupon_codes = [coupon.get("code") for coupon in woo_coupons]
        return {"woo_coupon": ", ".join(coupon_codes)}


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
        """Added dependencies for Product"""
        record = self.remote_record
        for line in record.get("line_items", []):
            lock_name = "import({}, {}, {}, {})".format(
                self.backend_record._name,
                self.backend_record.id,
                "woo.product.product",
                line["product_id"],
            )
            self.advisory_lock_or_retry(lock_name)
        for line in record.get("line_items", []):
            _logger.debug("line: %s", line)
            if "product_id" in line:
                self._import_dependency(line["product_id"], "woo.product.product")
        return super(WooSaleOrderImporter, self)._import_dependencies()


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

    def get_product(self, record):
        """Get The Binding of Product"""
        product_rec = record.get("product_id")
        if not product_rec:
            return False
        binder = self.binder_for("woo.product.product")
        product = binder.to_internal(product_rec, unwrap=True)
        return product

    @mapping
    def product_id(self, record):
        """Return Product excited in Woo order line and pre-check validations."""
        product_rec = record.get("product_id")
        if not product_rec:
            return {}
        product = self.get_product(record)
        return {"product_id": product.id, "product_uom": product.uom_id.id}

    @mapping
    def product_uom_qty(self, record):
        """Mapping for Product Uom qty"""
        product_qty = record.get("quantity")
        if not product_qty:
            product = self.get_product(record)
            error_message = (
                f"Order Line Product Quantity not found for Product: {product.name}"
            )
            raise MappingError(error_message)
        return {"product_uom_qty": product_qty}

    @mapping
    def price_unit(self, record):
        """Mapping for Price Unit"""
        unit_price = record.get("price")
        return {"price_unit": unit_price}

    @mapping
    def price_subtotal_line(self, record):
        """Mapping for Price Subtotal"""
        total = record.get("total")
        return {"price_subtotal_line": total} if total else {}

    @mapping
    def subtotal_line(self, record):
        """Mapping for Subtotal Line"""
        subtotal = record.get("subtotal")
        return {"subtotal_line": subtotal} if subtotal else {}

    @mapping
    def subtotal_tax_line(self, record):
        """Mapping for Subtotal Tax"""
        subtotal_tax = record.get("subtotal_tax")
        return {"subtotal_tax_line": subtotal_tax} if subtotal_tax else {}

    @mapping
    def total_tax_line(self, record):
        """Mapping for Total Tax Line"""
        total_tax = record.get("total_tax")
        return {"total_tax_line": total_tax} if total_tax else {}

    @mapping
    def name(self, record):
        """Mapping for Name"""
        name = record.get("name")
        if not name:
            raise MappingError(_("Order Line Name not found Please check!!!"))
        return {"name": name}

    @mapping
    def woo_order_id(self, record):
        """Mapping for Woo Order ID"""
        return {"woo_order_id": self.options.get("woo_order_id")}


class WooSaleOrderLineImporter(Component):
    _name = "woo.sale.order.line.importer"
    _inherit = "woo.map.child.import"
    _apply_on = "woo.sale.order.line"
