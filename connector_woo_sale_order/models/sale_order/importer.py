import logging

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping

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
        if self.backend_record.order_prefix:
            name = "{}{}".format(self.backend_record.order_prefix, record.get("id"))
        return {"name": name}

    @mapping
    def partner_id(self, record):
        """Return the partner_id ."""
        binder = self.binder_for("woo.res.partner")
        partner = binder.to_internal(record.get("customer_id"), unwrap=True)
        billing = record.get("billing")
        shipping = record.get("shipping")
        if partner:
            return {"partner_id": partner.id}
        else:
            if billing.get("first_name") or billing.get("email"):
                existing_partner = self.env["res.partner"].search(
                    [
                        ("firstname", "=", billing.get("first_name")),
                        ("lastname", "=", billing.get("last_name")),
                        ("email", "=", billing.get("email")),
                        ("street", "=", billing.get("address_1")),
                        ("street2", "=", billing.get("address_2")),
                        ("zip", "=", billing.get("postcode")),
                        ("phone", "=", billing.get("phone")),
                    ],
                    limit=1,
                )
                if not existing_partner:
                    billing_partner_data = {
                        "name": billing.get("first_name") or billing.get("email"),
                        "firstname": billing.get("first_name"),
                        "lastname": billing.get("last_name"),
                        "street": billing.get("address_1"),
                        "street2": billing.get("address_2"),
                        "city": billing.get("city"),
                        "zip": billing.get("postcode"),
                        "email": billing.get("email"),
                        "phone": billing.get("phone"),
                    }
                    billing_partner = self.env["res.partner"].create(
                        billing_partner_data
                    )
                    if shipping.get("first_name") or shipping.get("email"):
                        existing_partner_div = self.env["res.partner"].search(
                            [
                                ("firstname", "=", shipping.get("first_name")),
                                ("lastname", "=", shipping.get("last_name")),
                                ("email", "=", shipping.get("email")),
                                ("street", "=", shipping.get("address_1")),
                                ("street2", "=", shipping.get("address_2")),
                                ("zip", "=", shipping.get("postcode")),
                                ("phone", "=", shipping.get("phone")),
                            ],
                            limit=1,
                        )
                        if not existing_partner_div:
                            partner = self.env["res.partner"]
                            data = partner.child(record)
                            billing_partner.write({"child_ids": data})
                    return {"partner_id": billing_partner.id}
                else:
                    return {"partner_id": existing_partner.id}
            else:
                existing_partner = self.env["res.partner"].search(
                    [
                        ("firstname", "=", shipping.get("first_name")),
                        ("lastname", "=", shipping.get("last_name")),
                        ("email", "=", shipping.get("email")),
                        ("street", "=", shipping.get("address_1")),
                        ("street2", "=", shipping.get("address_2")),
                        ("zip", "=", shipping.get("postcode")),
                        ("street", "=", shipping.get("address_1")),
                        ("phone", "=", shipping.get("phone")),
                    ],
                    limit=1,
                )
                if not existing_partner:
                    child_partner_data = {
                        "name": shipping.get("first_name") or shipping.get("email"),
                        "firstname": shipping.get("first_name"),
                        "lastname": shipping.get("last_name"),
                        "street": shipping.get("address_1", ""),
                        "street2": shipping.get("address_2", ""),
                        "city": shipping.get("city", ""),
                        "zip": shipping.get("postcode", ""),
                        "email": shipping.get("email"),
                        "phone": shipping.get("phone"),
                    }
                    shipping_child_partner = self.env["res.partner"].create(
                        child_partner_data
                    )
                    partner = self.env["res.partner"]
                    data = partner.child(record)
                    shipping_child_partner.write({"child_ids": data})
                    return {"partner_id": shipping_child_partner.id}
                else:
                    return {"partner_id": existing_partner.id}

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
        return {"currency_id": record.get("currency")} if record.get("currency") else {}

    @mapping
    def total_tax(self, record):
        """Mapping for Total Tax"""
        return {"total_tax": record.get("total_tax")} if record.get("total_tax") else {}

    @mapping
    def amount_total(self, record):
        """Mapping for Amount Total"""
        return {"amount_total": record.get("total")} if record.get("total") else {}

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
    def product_uom(self, record):
        """Mapping for Product UOM"""
        return {"product_uom": 1}

    @mapping
    def product_id(self, record):
        """Return Product excited in Woo order line and pre-check validations."""
        binder = self.binder_for("woo.product.product")
        product = binder.to_internal(record.get("product_id"), unwrap=True)
        return {"product_id": product.id} if record.get("product_id") else {}

    @mapping
    def product_uom_qty(self, record):
        """Mapping for Product Uom qty"""
        return {"product_uom_qty": record.get("quantity")}

    @mapping
    def price_unit(self, record):
        """Mapping for Price Unit"""
        return {"price_unit": record.get("price")}

    @mapping
    def tax_id(self, record):
        """Mapping for Tax"""
        tax_ids = []
        total_tax = record.get("taxes")
        if total_tax:
            tax_id_list = total_tax.split(",")
            tax_ids = [int(tax_id) for tax_id in tax_id_list]
        return {"tax_id": [(6, 0, tax_ids)]}

    @mapping
    def price_subtotal(self, record):
        """Mapping for Price Subtotal"""
        return {"price_subtotal": record.get("total")}

    @mapping
    def name(self, record):
        """Mapping for Name"""
        return {"name": record.get("name")}

    @mapping
    def order_id(self, record):
        """Mapping for Order"""
        order_id = self.options.get("order_id")
        return {"order_id": order_id}

    @mapping
    def backend_id(self, record):
        """Return backend."""
        return {"backend_id": self.backend_record.id}


class WooSaleOrderLineImporter(Component):
    _name = "woo.sale.order.line.importer"
    _inherit = "woo.map.child.import"
    _apply_on = "woo.sale.order.line"
