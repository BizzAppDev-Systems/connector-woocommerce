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
    def firstname(self, record):
        """Mapping for name"""
        first_name = record.get("first_name")
        username = record.get("username")
        email = record.get("email")
        firstname_value = first_name or username or email
        return {"firstname": firstname_value}

    @mapping
    def lastname(self, record):
        """Mapping for name"""
        return {"lastname": record.get("last_name")} if record.get("last_name") else {}

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
        return {"email": email}

    @only_create
    @mapping
    def child_ids(self, record):
        """Mapping for Invoice and Shipping Addresses"""
        billing = record.get("billing")
        shipping = record.get("shipping")
        state = billing.get("state")
        child_ids_data = []
        if state:
            state = self.env["res.country.state"].search(
                [("code", "=", state)],
                limit=1,
            )
        fields_to_check = ["first_name", "last_name", "email"]
        for data, address_type in [(billing, "invoice"), (shipping, "delivery")]:
            if any(data.get(field) for field in fields_to_check):
                address_data = self.env["res.partner"].create(
                    {
                        "firstname": data.get("first_name") or data.get("email"),
                        "lastname": data.get("last_name"),
                        "email": data.get("email"),
                        "type": address_type,
                        "street": data.get("address_1"),
                        "street2": data.get("address_2"),
                        "zip": data.get("postcode"),
                        "state_id": state.id if state else False,
                    }
                )
                child_ids_data.append((4, address_data.id))
        return {"child_ids": child_ids_data}

    @mapping
    def backend_id(self, record):
        """Return backend."""
        return {"backend_id": self.backend_record.id}


class WooResPartnerImporter(Component):
    """Importer the WooCommerce Partner"""

    _name = "woo.res.partner.importer"
    _inherit = "woo.importer"
    _apply_on = "woo.res.partner"
