import logging

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from odoo.addons.connector.exception import MappingError

# pylint: disable=W7950

_logger = logging.getLogger(__name__)


class WooResPartnerBatchImporter(Component):
    """Batch Importer for WooCommerce Partners"""

    _name = "woo.res.partner.batch.importer"
    _inherit = "woo.batch.importer"
    _apply_on = "woo.res.partner"


class WooResPartnerImportMapper(Component):
    """Impoter Mapper for the WooCommerce Partner"""

    _name = "woo.res.partner.import.mapper"
    _inherit = "woo.import.mapper"
    _apply_on = "woo.res.partner"

    @mapping
    def name(self, record):
        """Mapping for Name (combination of firstname and lastname)"""
        first_name = record.get("first_name", "")
        last_name = record.get("last_name", "")
        username = record.get("username", "")
        name = f"{first_name} {last_name}" if first_name or last_name else username
        if not name:
            raise MappingError(_("Username not found!"))
        return {"name": name.strip()}

    @mapping
    def firstname(self, record):
        """Mapping for firstname"""
        return (
            {"firstname": record.get("first_name")} if record.get("first_name") else {}
        )

    @mapping
    def lastname(self, record):
        """Mapping for lastname"""
        return {"lastname": record.get("last_name")} if record.get("last_name") else {}

    @mapping
    def email(self, record):
        """Mapping for Email"""
        email = record.get("email")
        if not email:
            raise MappingError(_("No Email found in Response"))
        return {"email": email}

    @mapping
    def country_id(self, record):
        billing = record.get("billing")
        shipping = record.get("shipping")
        if any(billing.values()):
            woo_country = billing.get("country")
            country = self.env["res.country"].search(
                [("code", "=", woo_country)], limit=1
            )
            return {"country_id": country.id}
        elif any(shipping.values()):
            woo_state = billing.get("state")
            country = self.env["res.country"].search(
                [("code", "=", woo_state)], limit=1
            )
            return {"country_id": country.id}
        else:
            return {}

    @mapping
    def state_id(self, record):
        billing = record.get("billing")
        shipping = record.get("shipping")
        if any(billing.values()):
            woo_state = billing.get("state")
            woo_country = billing.get("country")
            country_record = self.env["res.country"].search(
                [("code", "=", woo_country)],
                limit=1,
            )
            state = self.env["res.country.state"].search(
                [("code", "=", woo_state), ("country_id", "=", country_record.id)],
                limit=1,
            )
            return {"state_id": state.id}
        elif any(shipping.values()):
            woo_state = shipping.get("state")
            woo_country = shipping.get("shipping")
            country_record = self.env["res.country"].search(
                [("code", "=", woo_country)],
                limit=1,
            )
            state = self.env["res.country.state"].search(
                [("code", "=", woo_state), ("country_id", "=", country_record.id)],
                limit=1,
            )
            return {"state_id": state.id}
        else:
            return {}

    @mapping
    def street(self, record):
        billing = record.get("billing")
        shipping = record.get("shipping")
        if any(billing.values()):
            woo_address = billing.get("address_1")
            return {"street": woo_address}
        elif any(shipping.values()):
            woo_address = billing.get("address_1")
            return {"street": woo_address}
        else:
            return {}

    @mapping
    def street2(self, record):
        billing = record.get("billing")
        shipping = record.get("shipping")
        if any(billing.values()):
            woo_address2 = billing.get("address_2")
            return {"street2": woo_address2}
        elif any(shipping.values()):
            woo_address2 = billing.get("address_2")
            return {"street2": woo_address2}
        else:
            return {}

    @mapping
    def zip(self, record):
        billing = record.get("billing")
        shipping = record.get("shipping")
        if any(billing.values()):
            woo_zip = billing.get("zip")
            return {"zip": woo_zip}
        elif any(shipping.values()):
            woo_zip = billing.get("zip")
            return {"zip": woo_zip}
        else:
            return {}

    @mapping
    def city(self, record):
        billing = record.get("billing")
        shipping = record.get("shipping")
        if any(billing.values()):
            woo_city = billing.get("city")
            return {"city": woo_city}
        elif any(shipping.values()):
            woo_city = billing.get("city")
            return {"zip": woo_city}
        else:
            return {}

    @mapping
    def addresses(self, record):
        """Mapping for Invoice and Shipping Addresses"""
        woo_res_partner = self.env["res.partner"]
        child_data = woo_res_partner.create_get_children(
            record, record.get("id"), self.backend_record
        )
        return (
            {"child_ids": [(0, 0, child_added) for child_added in child_data]}
            if child_data
            else {}
        )


class WooResPartnerImporter(Component):
    """Importer the WooCommerce Partner"""

    _name = "woo.res.partner.importer"
    _inherit = "woo.importer"
    _apply_on = "woo.res.partner"
