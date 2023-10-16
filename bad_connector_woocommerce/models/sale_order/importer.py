import logging

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create
from odoo.addons.connector.exception import MappingError

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

    def _prepare_lines(self, product, price, qty, ext_id, description="", total_tax=0):
        """Prepare lines of shipping"""
        vals = {
            "product_id": product.id,
            "price_unit": price,
            "product_uom_qty": qty,
            "product_uom": product.uom_id.id,
            "backend_id": self.backend_record.id,
            "external_id": ext_id,
            "total_tax_line": total_tax,
        }
        if description:
            vals.update({"name": description})
        return vals

    def _get_shipping_lines(self, map_record, values):
        """Get the Shipping Lines"""
        shipping_lines = []
        record = map_record.source
        shipping_id = False
        for shipping_line in record.get("shipping_lines", []):
            shipping_values = {"is_delivery": True}
            woo_shipping_id = shipping_line.get("method_id")
            if not woo_shipping_id:
                shipping_id = self.backend_record.default_shipping_method_id
                if not shipping_id:
                    raise MappingError(
                        _("The default shipping method must be set on the backend")
                    )
            else:
                binder = self.binder_for("woo.delivery.carrier")
                shipping_id = binder.to_internal(woo_shipping_id, unwrap=True)

            shipping_values.update(
                self._prepare_lines(
                    shipping_id.product_id,
                    shipping_line.get("total"),
                    1,
                    shipping_line.get("id"),
                    shipping_line.get("method_title"),
                    shipping_line.get("total_tax"),
                )
            )
            shipping_lines.append((0, 0, shipping_values))
        return shipping_id, shipping_lines

    def _get_fee_lines(self, map_record, values):
        """Get fee lines"""
        fee_lines = []
        record = map_record.source
        for fee_line in record.get("fee_lines", []):
            fee_product = self.backend_record.default_fee_product_id
            if not fee_product:
                raise MappingError(
                    _("The default fee product must be set on the backend")
                )
            fee_lines.append(
                (
                    0,
                    0,
                    self._prepare_lines(
                        fee_product,
                        fee_line.get("total"),
                        1,
                        fee_line.get("id"),
                        fee_line.get("name"),
                        fee_line.get("total_tax"),
                    ),
                )
            )
        return fee_lines

    def finalize(self, map_record, values):
        """Inherit the method to add the shipping and fee product lines."""
        shipping_id, shipping_lines = self._get_shipping_lines(map_record, values)
        woo_order_line_ids = values.get("woo_order_line_ids", [])
        if shipping_lines:
            woo_order_line_ids += shipping_lines
        if shipping_id:
            values.update({"carrier_id": shipping_id.id})
        fee_lines = self._get_fee_lines(map_record, values)
        if fee_lines:
            woo_order_line_ids += fee_lines
        values.update({"woo_order_line_ids": woo_order_line_ids})
        return super(WooSaleOrderImportMapper, self).finalize(map_record, values)

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
        self.options.update(woo_order_id=woo_order_id, order_record=record)
        return {"woo_order_id": woo_order_id}

    @mapping
    def company_id(self, record):
        """Mapping for company id"""
        return {"company_id": self.backend_record.company_id.id}

    @mapping
    def team_id(self, record):
        """Mapping for team_id"""
        sale_team_id = self.backend_record.sale_team_id.id
        return {"team_id": sale_team_id} if sale_team_id else {}

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

    def _must_skip(self, **kwargs):
        """Skipped Record which are already imported."""
        if self.binder.to_internal(self.external_id):
            return _("Already imported")
        return super(WooSaleOrderImporter, self)._must_skip(**kwargs)

    def _import_dependencies(self, **kwargs):
        """
        Override method to import dependencies for WooCommerce sale order.
        This method is overridden to handle the import of dependencies, particularly for
        WooCommerce sale orders. It retrieves line items from the remote record and imports
        the associated products as dependencies, ensuring that they are available for
        the sale order.
        """
        record = self.remote_record
        for line in record.get("line_items", []):
            lock_name = "import({}, {}, {}, {})".format(
                self.backend_record._name,
                self.backend_record.id,
                "woo.product.product",
                line["product_id"],
            )
            self.advisory_lock_or_retry(lock_name)
            for tax in line.get("taxes", []):
                lock_name = "import({}, {}, {}, {})".format(
                    self.backend_record._name,
                    self.backend_record.id,
                    "woo.tax",
                    tax["id"],
                )
                self.advisory_lock_or_retry(lock_name)
        for shipping_line in record.get("shipping_lines", []):
            lock_name = "import({}, {}, {}, {})".format(
                self.backend_record._name,
                self.backend_record.id,
                "woo.delivery.carrier",
                shipping_line["method_id"],
            )
            self.advisory_lock_or_retry(lock_name)
        for line in record.get("line_items", []):
            _logger.debug("line: %s", line)
            if "product_id" in line:
                self._import_dependency(line["product_id"], "woo.product.product")
            for tax in line.get("taxes", []):
                self._import_dependency(tax["id"], "woo.tax")

        for shipping_line in record.get("shipping_lines", []):
            _logger.debug("shipping_line: %s", shipping_line)
            if "method_id" in shipping_line:
                self._import_dependency(
                    shipping_line["method_id"], "woo.delivery.carrier"
                )
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
        """Mapping for Subtotal Tax Line"""
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

    def fetch_list_of_tax(self, taxes, tax_lines):
        """
        Fetch tax IDs based on the provided taxes and tax lines.
        """
        result = []
        fetched_taxes = {}
        tax_binder = self.binder_for(model="woo.tax")
        for tax in taxes:
            woo_tax = tax_binder.to_internal(tax.get("id"))
            if woo_tax and woo_tax.odoo_id:
                result.append(woo_tax.odoo_id.id)
                continue
            rate_id = tax.get("id")
            tax_line = next(
                (tl for tl in tax_lines if tl.get("rate_id") == rate_id), None
            )
            if woo_tax and not tax_line:
                continue
            rate_percent = tax_line.get("rate_percent")
            company = self.backend_record.company_id
            if rate_percent not in fetched_taxes:
                search_conditions = [
                    ("amount", "=", rate_percent),
                    ("type_tax_use", "in", ["sale", "none"]),
                    ("company_id", "=", company.id),
                ]
                tax = self.env["account.tax"].search(search_conditions, limit=1)
                if not tax:
                    continue
                result.append(tax.id)
                fetched_taxes[rate_percent] = tax
                continue
            result.append(fetched_taxes[rate_percent].id)
        return result

    @mapping
    def tax_id(self, record):
        """
        Mapping for Tax_id. Calls fetch_list_of_tax method to
        fetch or create tax IDs.
        """
        tax_lines = self.options.get("order_record", {}).get("tax_lines", [])
        taxes = record.get("taxes", [])
        tax_ids = self.fetch_list_of_tax(taxes, tax_lines)
        return {"tax_id": [(6, 0, tax_ids)]}

    @mapping
    def woo_order_id(self, record):
        """Mapping for Woo Order ID"""
        return {"woo_order_id": self.options.get("woo_order_id")}


class WooSaleOrderLineImporter(Component):
    _name = "woo.sale.order.line.importer"
    _inherit = "woo.map.child.import"
    _apply_on = "woo.sale.order.line"
