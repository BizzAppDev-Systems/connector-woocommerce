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
        if record.get("email"):
            return {"email": record.get("email")}
        elif record.get("billing").get("email"):
            return {"email": record.get("billing").get("email")}
        else:
            return {"email": record.get("shipping").get("email")}

    @mapping
    def street(self, record):
        """Mapping for street"""
        if record.get("billing", {}).get("address_1"):
            return {"street": record.get("billing", {}).get("address_1")}
        elif record.get("shipping", {}).get("address_1"):
            return {"street": record.get("shipping", {}).get("address_1")}
        else:
            return {}

    @mapping
    def street2(self, record):
        """Mapping for street2"""
        if record.get("billing", {}).get("address_2"):
            return {"street2": record.get("billing", {}).get("address_2")}
        elif record.get("shipping", {}).get("address_2"):
            return {"street2": record.get("shipping", {}).get("address_2")}
        else:
            return {}

    @mapping
    def city(self, record):
        """Mapping for city"""
        if record.get("billing", {}).get("city"):
            return {"city": record.get("billing", {}).get("city")}
        elif record.get("shipping", {}).get("city"):
            return {"city": record.get("shipping", {}).get("city")}
        else:
            return {}

    @mapping
    def state_id(self, record):
        """Mapping for state"""
        state = self.env["res.country.state"].search(
            [("code", "=", record.get("billing", {}).get("state"))],
            limit=1,
        )
        if state:
            return {"state_id": state.id}
        elif record.get("shipping", {}).get("state"):
            state_shipping = self.env["res.country.state"].search(
                [("code", "=", record.get("shipping", {}).get("state"))],
                limit=1,
            )
            if state_shipping:
                return {"state_id": state_shipping.id}
        else:
            return {}

    @mapping
    def country_id(self, record):
        """Mapping for country"""
        country = self.env["res.country"].search(
            [("code", "=", record.get("billing", {}).get("country"))],
            limit=1,
        )
        if country:
            return {"country_id": country.id}
        elif record.get("shipping", {}).get("country"):
            country_shipping = self.env["res.country"].search(
                [("code", "=", record.get("shipping", {}).get("country"))],
                limit=1,
            )
            if country_shipping:
                return {"country_id": country_shipping.id}
        else:
            return {}

    @mapping
    def phone(self, record):
        """Mapping for phone"""
        if record.get("billing", {}).get("phone"):
            return {"phone": record.get("billing", {}).get("phone")}
        elif record.get("shipping", {}).get("phone"):
            return {"phone": record.get("shipping", {}).get("phone")}
        else:
            return {}

    @mapping
    def zip(self, record):
        """Mapping for zip"""
        if record.get("billing", {}).get("postcode"):
            return {"zip": record.get("billing", {}).get("postcode")}
        elif record.get("shipping", {}).get("postcode"):
            return {"zip": record.get("shipping", {}).get("postcode")}
        else:
            return {}

    @mapping
    def company_id(self, record):
        """Mapping for company"""
        if record.get("billing", {}).get("company"):
            return {"company_id": record.get("billing", {}).get("company")}
        elif record.get("shipping", {}).get("company"):
            return {"company_id": record.get("shipping", {}).get("company")}
        else:
            return {}

    @mapping
    def backend_id(self, record):
        """Return backend."""
        return {"backend_id": self.backend_record.id}


class WooResPartnerImporter(Component):
    """Importer the WooCommerce Partner"""

    _name = "woo.res.partner.importer"
    _inherit = "woo.importer"
    _apply_on = "woo.res.partner"
