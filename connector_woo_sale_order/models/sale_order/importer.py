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

    @mapping
    def partner_id(self, record):
        """Return the partner_id ."""
        binder = self.binder_for("woo.res.partner")
        partner = binder.to_internal(record.get("customer_id"), unwrap=True)
        billing = record.get("billing")
        shipping = record.get("shipping")
        if partner:
            return {"partner_id": partner.id}
        if not billing or not shipping:
            return {}
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
                    # if shipping:
                    #     existing_delivery_partner = self.env["res.partner"].search(
                    #         [
                    #             ("firstname", "=", shipping.get("first_name")),
                    #             ("lastname", "=", shipping.get("last_name")),
                    #             ("email", "=", shipping.get("email")),
                    #             ("street", "=", shipping.get("address_1")),
                    #             ("street2", "=", shipping.get("address_2")),
                    #             ("type", "=", "delivery"),
                    #             ("zip", "=", shipping.get("postcode")),
                    #             ("street", "=", shipping.get("address_1")),
                    #             ("phone", "=", shipping.get("phone")),
                    #         ],
                    #         limit=1,
                    #     )
                    #     if not existing_delivery_partner:
                    # billing_partner = {
                    #     "firstname": billing.get("first_name"),
                    #     "lastname": billing.get("last_name"),
                    #     "street": billing.get("address_1", ""),
                    #     "street2": billing.get("address_2", ""),
                    #     "city": billing.get("city", ""),
                    #     "type": "delivery",
                    #     "zip": billing.get("postcode", ""),
                    #     "email": billing.get("email"),
                    #     "phone": billing.get("phone"),
                    # }
                    # self.env["res.partner"].create(billing_partner)
                    # else:
                    #     existing_delivery_partner = self.env["res.partner"].search(
                    #         [
                    #             ("firstname", "=", shipping.get("first_name")),
                    #             ("lastname", "=", shipping.get("last_name")),
                    #             ("email", "=", shipping.get("email")),
                    #             ("street", "=", shipping.get("address_1")),
                    #             ("street2", "=", shipping.get("address_2")),
                    #             ("type", "=", "delivery"),
                    #             ("zip", "=", shipping.get("postcode")),
                    #             ("street", "=", shipping.get("address_1")),
                    #             ("phone", "=", shipping.get("phone")),
                    #         ],
                    #         limit=1,
                    #     )
                    # if existing_delivery_partner:
                    #     return {"partner_id": existing_partner.id}
                    # else:
                    #     billing_partner = {
                    #         "firstname": billing.get("first_name"),
                    #         "lastname": billing.get("last_name"),
                    #         "street": billing.get("address_1", ""),
                    #         "street2": billing.get("address_2", ""),
                    #         "city": billing.get("city", ""),
                    #         "type": "invoice",
                    #         "zip": billing.get("postcode", ""),
                    #         "email": billing.get("email"),
                    #         "phone": billing.get("phone"),
                    #     }
                    #     partner = self.env["res.partner"].create(billing_partner)
                    #     return {"partner_id": partner.id}
                    # return {"partner_id": billing_partner_created.id}
        # elif shipping:
        #     shiping_partner = {
        #         "name": shipping.get("first_name") + " " + shipping.get("last_name"),
        #         "street": shipping.get("address_1", ""),
        #         "street2": shipping.get("address_2", ""),
        #         "city": shipping.get("city", ""),
        #         "zip": shipping.get("postcode", ""),
        #         "email": shipping.get("email"),
        #         "phone": shipping.get("phone"),
        #     }
        #     partner = self.env["res.partner"].create(shiping_partner)

    # return {"partner_id": partner.id}
    # @mapping
    # def partner_id(self, record):
    #     """Return the partner_id."""
    #     binder = self.binder_for("woo.res.partner")
    #     partner = binder.to_internal(record.get("customer_id"), unwrap=True)
    #     if not partner:
    #         billing_info = record.get("billing", {})
    #         existing_partner = self.env["res.partner"].search(
    #             [
    #                 ("name", "=", billing_info.get("first_name")),
    #                 ("woo_customer_id", "=", False),
    #             ],
    #             limit=1,
    #         )

    #         if existing_partner:
    #             partner = existing_partner
    #         else:
    #             partner_vals = {
    #                 "firstname": billing_info.get("first_name"),
    #                 "lastname": billing_info.get("last_name"),
    #                 "woo_customer_id": record.get("customer_id"),
    #                 "street": billing_info.get("address_1", ""),
    #                 "street2": billing_info.get("address_2", ""),
    #                 "city": billing_info.get("city", ""),
    #                 "zip": billing_info.get("postcode", ""),
    #                 "state_id": self.map_state_id(
    #                     billing_info.get("state"), billing_info.get("country")
    #                 ),
    #                 "country_id": self.map_country_id(billing_info.get("country")),
    #             }
    #             partner = self.env["res.partner"].create(partner_vals)

    #     return {"partner_id": partner.id}

    @mapping
    def discount_total(self, record):
        print(record.get("discount_total"))
        return {"discount_total": record.get("discount_total")}

    @mapping
    def discount_tax(self, record):
        print(record.get("discount_tax"))
        return {"discount_tax": record.get("discount_tax")}

    @mapping
    def shipping_total(self, record):
        print(record.get("shipping_total"))
        return {"shipping_total": record.get("shipping_total")}

    @mapping
    def shipping_tax(self, record):
        print(record.get("shipping_tax"))
        return {"shipping_tax": record.get("shipping_tax")}

    @mapping
    def cart_tax(self, record):
        print(record.get("cart_tax"))
        return {"cart_tax": record.get("cart_tax")}

    @mapping
    def currency_id(self, record):
        print(record.get("currency"))
        return {"currency_id": record.get("currency")}

    @mapping
    def total_tax(self, record):
        print(record.get("total_tax"))
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
