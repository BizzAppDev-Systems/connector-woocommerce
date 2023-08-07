import logging

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create

# pylint: disable=W7950

_logger = logging.getLogger(__name__)


class WooResPartnerBatchImporter(Component):
    """Batch Importer the WooCommerce Partner"""

    _name = "woo.res.partner.batch.importer"
    _inherit = "woo.delayed.batch.importer"
    _apply_on = "woo.res.partner"


class WooResPartnerImportMapper(Component):
    """Impoter Mapper for the WooCommerce Partner"""

    _name = "woo.res.partner.import.mapper"
    _inherit = "woo.import.mapper"
    _apply_on = "woo.res.partner"

    _sql_constraints = [
        ("woo_res_partner_email_unique", "UNIQUE(email)", "Email must be unique!")
    ]

    @only_create
    @mapping
    def name(self, record):
        """Mapping for name"""
        if record.get("username"):
            return {"name": record.get("username")}
        elif record.get("billing").get("first_name"):
            return {
                "name": "{} {}".format(
                    record.get("billing").get("first_name"),
                    record.get("billing").get("last_name"),
                )
            }
        else:
            return {
                "name": "{} {}".format(
                    record.get("shipping").get("first_name"),
                    record.get("shipping").get("last_name"),
                )
            }

    @only_create
    @mapping
    def odoo_id(self, record):
        """Will bind the partner to an existing one with the same code"""
        binder = self.binder_for(model="woo.res.partner")
        woo_partner = binder.to_internal(record.get("id"), unwrap=True)
        if woo_partner:
            return {"odoo_id": woo_partner.id}
        return {}

    @mapping
    def email(self, record):
        """Mapping for Email"""
        email = record.get("email")
        billing_address = record.get("billing", {})
        shipping_address = record.get("shipping", {})
        email = email or billing_address.get("email") or shipping_address.get("email")
        return {"email": email} if email else {}

    @mapping
    def street(self, record):
        """Mapping for street"""
        billing_address = record.get("billing", {})
        shipping_address = record.get("shipping", {})
        street = billing_address.get("address_1") or shipping_address.get("address_1")
        return {"street": street} if street else {}

    @mapping
    def street2(self, record):
        """Mapping for street2"""
        billing_address = record.get("billing", {})
        shipping_address = record.get("shipping", {})
        street2 = billing_address.get("address_2") or shipping_address.get("address_2")
        return {"street2": street2} if street2 else {}

    @mapping
    def city(self, record):
        """Mapping for city"""
        billing_address = record.get("billing", {})
        shipping_address = record.get("shipping", {})
        city = billing_address.get("city") or shipping_address.get("city")
        return {"city": city} if city else {}

    @mapping
    def state_id(self, record):
        """Mapping for state"""
        state_code = record.get("billing", {}).get("state") or record.get(
            "shipping", {}
        ).get("state")
        if state_code:
            state = self.env["res.country.state"].search(
                [("code", "=", state_code)],
                limit=1,
            )
            if state:
                return {"state_id": state.id}
        return {}

    @mapping
    def country_id(self, record):
        """Mapping for country"""
        billing_country_code = record.get("billing", {}).get("country")
        shipping_country_code = record.get("shipping", {}).get("country")
        country_code = billing_country_code or shipping_country_code
        if country_code:
            country = self.env["res.country"].search(
                [("code", "=", country_code)],
                limit=1,
            )
            if country:
                return {"country_id": country.id}
        return {}

    @mapping
    def phone(self, record):
        """Mapping for phone"""
        billing_address = record.get("billing", {})
        shipping_address = record.get("shipping", {})
        phone = billing_address.get("phone") or shipping_address.get("phone")
        return {"phone": phone} if phone else {}

    @mapping
    def zip(self, record):
        """Mapping for zip"""
        billing_address = record.get("billing", {})
        shipping_address = record.get("shipping", {})
        postcode = billing_address.get("postcode") or shipping_address.get("postcode")
        return {"zip": postcode} if postcode else {}

    @mapping
    def company_id(self, record):
        """Mapping for company"""
        billing_address = record.get("billing", {})
        shipping_address = record.get("shipping", {})
        company = billing_address.get("company") or shipping_address.get("company")
        return {"company_id": company} if company else {}

    @mapping
    def backend_id(self, record):
        """Return backend."""
        return {"backend_id": self.backend_record.id}


class WooResPartnerImporter(Component):
    """Importer the WooCommerce Partner"""

    _name = "woo.res.partner.importer"
    _inherit = "woo.importer"
    _apply_on = "woo.res.partner"
