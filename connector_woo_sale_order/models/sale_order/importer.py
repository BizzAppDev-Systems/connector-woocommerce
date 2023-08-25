import logging

from odoo.addons.component.core import Component
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
        if self.backend_record.order_prefix:
            name = "{}{}".format(self.backend_record.order_prefix, record.get("id"))
        return {"name": name}

    @mapping
    def odoo_id(self, record):
        """Will bind the Sale order to an existing one with the same code"""
        binder = self.binder_for(model="woo.sale.order")
        woo_order = binder.to_internal(record.get("id"), unwrap=True)
        if woo_order:
            return {"odoo_id": woo_order.id}
        return {}

    def _has_non_empty_billing(self, billing_data):
        """Check if billing information has any non-empty fields."""
        return all(value for value in billing_data.values())

    def _find_existing_partner(self, partner_data, partner_type):
        """Search for an existing partner based on provided data."""
        existing_partner = self.env["res.partner"].search(
            [
                ("firstname", "=", partner_data.get("first_name")),
                ("lastname", "=", partner_data.get("last_name")),
                ("email", "=", partner_data.get("email")),
                ("street", "=", partner_data.get("address_1")),
                ("street2", "=", partner_data.get("address_2")),
                ("type", "=", partner_type),
                ("zip", "=", partner_data.get("postcode")),
                ("phone", "=", partner_data.get("phone")),
            ],
            limit=1,
        )
        return existing_partner

    def _create_partner(self, partner_data, partner_type):
        """Create a new partner based on provided data."""
        partner = self.env["res.partner"].create(
            {
                "firstname": partner_data.get("first_name"),
                "lastname": partner_data.get("last_name"),
                "street": partner_data.get("address_1"),
                "street2": partner_data.get("address_2"),
                "city": partner_data.get("city"),
                "zip": partner_data.get("postcode"),
                "email": partner_data.get("email"),
                "phone": partner_data.get("phone"),
                "type": partner_type,
            }
        )
        return partner

    @mapping
    def partner_id(self, record):
        """Return the partner_id."""
        binder = self.binder_for("woo.res.partner")
        partner = binder.to_internal(record.get("customer_id"), unwrap=True)

        if partner:
            return {"partner_id": partner.id}

        billing = record.get("billing")
        shipping = record.get("shipping")

        if billing and self._has_non_empty_billing(billing):
            existing_billing_partner = self._find_existing_partner(billing, "invoice")
            if not existing_billing_partner:
                billing_partner = self._create_partner(billing, "invoice")

                if shipping:
                    existing_shipping_partner = self._find_existing_partner(
                        shipping, "delivery"
                    )
                    if not existing_shipping_partner:
                        shipping_partner = self._create_partner(shipping, "delivery")
                        billing_partner.child_ids = [(4, shipping_partner.id)]
                return {"partner_id": billing_partner.id}
        elif shipping and self._has_non_empty_billing(shipping):
            existing_shipping_partner = self._find_existing_partner(
                shipping, "delivery"
            )
            if not existing_shipping_partner:
                shipping_partner = self._create_partner(shipping, "delivery")
                return {"partner_id": shipping_partner.id}
        return {}

    @mapping
    def partner_id(self, record):
        """Return the partner_id ."""
        binder = self.binder_for("woo.res.partner")
        partner = binder.to_internal(record.get("customer_id"), unwrap=True)
        billing = record.get("billing")
        shipping = record.get("shipping")
        if partner:
            return {"partner_id": partner.id}
        # if not billing or not shipping:
        #     return {}
        else:
            if billing:
                existing_partner = self.env["res.partner"].search(
                    [
                        ("firstname", "=", billing.get("first_name")),
                        ("lastname", "=", billing.get("last_name")),
                        ("email", "=", billing.get("email")),
                        ("street", "=", billing.get("address_1")),
                        ("street2", "=", billing.get("address_2")),
                        ("type", "=", "invoice"),
                        ("zip", "=", billing.get("postcode")),
                        ("street", "=", billing.get("address_1")),
                        ("phone", "=", billing.get("phone")),
                    ],
                    limit=1,
                )
                if not existing_partner:
                    billing_partner_data = {
                        "firstname": billing.get("first_name"),
                        "lastname": billing.get("last_name"),
                        "street": billing.get("address_1"),
                        "street2": billing.get("address_2"),
                        "city": billing.get("city"),
                        "zip": billing.get("postcode"),
                        "email": billing.get("email"),
                        "phone": billing.get("phone"),
                        "type": "invoice",
                    }
                    billing_partner = self.env["res.partner"].create(
                        billing_partner_data
                    )
                    if shipping:
                        existing_partner = self.env["res.partner"].search(
                            [
                                ("firstname", "=", shipping.get("first_name")),
                                ("lastname", "=", shipping.get("last_name")),
                                ("email", "=", shipping.get("email")),
                                ("street", "=", shipping.get("address_1")),
                                ("street2", "=", shipping.get("address_2")),
                                ("type", "=", "delivery"),
                                ("zip", "=", shipping.get("postcode")),
                                ("street", "=", shipping.get("address_1")),
                                ("phone", "=", shipping.get("phone")),
                            ],
                            limit=1,
                        )
                        if not existing_partner:
                            child_partner_data = {
                                "firstname": shipping.get("first_name"),
                                "lastname": shipping.get("last_name"),
                                "street": shipping.get("address_1", ""),
                                "street2": shipping.get("address_2", ""),
                                "city": shipping.get("city", ""),
                                "zip": shipping.get("postcode", ""),
                                "email": shipping.get("email"),
                                "phone": shipping.get("phone"),
                                "type": "delivery",
                            }
                            child_partner = self.env["res.partner"].create(
                                child_partner_data
                            )
                    delivery_partner_data = {
                        "firstname": shipping.get("first_name"),
                        "lastname": shipping.get("last_name"),
                        "street": shipping.get("address_1"),
                        "street2": shipping.get("address_2"),
                        "city": shipping.get("city"),
                        "zip": shipping.get("postcode"),
                        "email": shipping.get("email"),
                        "phone": shipping.get("phone"),
                        "type": "delivery",  # Indicating this is a delivery-related partner
                    }

                    # Create the child partner for delivery
                    delivery_partner = self.env["res.partner"].create(
                        delivery_partner_data
                    )
                billing_partner.child_ids = [(4, child_partner.id)]
                return {"partner_id": billing_partner.id}

    @mapping
    def discount_total(self, record):
        return {"discount_total": record.get("discount_total")}

    @mapping
    def discount_tax(self, record):
        return {"discount_tax": record.get("discount_tax")}

    @mapping
    def shipping_total(self, record):
        return {"shipping_total": record.get("shipping_total")}

    @mapping
    def shipping_tax(self, record):
        return {"shipping_tax": record.get("shipping_tax")}

    @mapping
    def cart_tax(self, record):
        return {"cart_tax": record.get("cart_tax")}

    @mapping
    def currency_id(self, record):
        return {"currency_id": record.get("currency")}

    @mapping
    def total_tax(self, record):
        return {"total_tax": record.get("total_tax")}

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

    @mapping
    def update_order_id(self, record):
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
        return {"product_uom": 1}

    @mapping
    def odoo_id(self, record):
        """Return sale order line."""
        binder = self.binder_for(model="woo.sale.order.line")
        woo_order = binder.to_internal(record.get("id"), unwrap=True)
        return {"odoo_id": woo_order.id} if woo_order else {}

    @mapping
    def product_id(self, record):
        """Return Product excited in Woo order line and pre-check validations."""
        binder = self.binder_for("woo.product.product")
        if not record.get("product_id"):
            return {}
        product = binder.to_internal(record.get("product_id"), unwrap=True)
        return {"product_id": product.id}

    @mapping
    def product_uom_qty(self, record):
        return {"product_uom_qty": record.get("quantity")}

    @mapping
    def price_unit(self, record):
        return {"price_unit": record.get("price")}

    @mapping
    def tax_id(self, record):
        tax_ids = []
        total_tax = record.get("taxes")
        if total_tax:
            tax_id_list = total_tax.split(",")
            tax_ids = [int(tax_id) for tax_id in tax_id_list]

        return {"tax_id": [(6, 0, tax_ids)]}

    @mapping
    def price_subtotal(self, record):
        return {"price_subtotal": record.get("total")}

    @mapping
    def name(self, record):
        return {"name": record.get("name")}

    @mapping
    def order_id(self, record):
        order_id = self.options.get("order_id")
        return {"order_id": order_id}

    @mapping
    def external_id(self, record):
        """Return external id."""
        return {"external_id": record.get("id")}

    @mapping
    def backend_id(self, record):
        """Return backend."""
        return {"backend_id": self.backend_record.id}


class WooSaleOrderLineImporter(Component):
    _name = "woo.sale.order.line.importer"
    _inherit = "woo.map.child.import"
    _apply_on = "woo.sale.order.line"
