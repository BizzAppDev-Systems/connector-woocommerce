import hashlib
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

    @mapping
    def name(self, record):
        """Mapping for Name (combination of firstname and lastname)"""
        first_name = record.get("first_name", "")
        last_name = record.get("last_name", "")
        full_name = (
            f"{first_name} {last_name}"
            if first_name and last_name
            else first_name or last_name or record.get("username", "")
        )
        return {"name": full_name}

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
    def odoo_id(self, record):
        """Will bind the partner to an existing one with the same code"""
        binder = self.binder_for(model="woo.res.partner")
        woo_partner = binder.to_internal(record.get("id"), unwrap=True)
        return {"odoo_id": woo_partner.id} if woo_partner else {}

    @mapping
    def email(self, record):
        """Mapping for Email"""
        email = record.get("email")
        if not email:
            raise MappingError(_("No Email found in Response"))
        return {"email": email}

    def _prepare_partner_vals(self, data, address_type, state):
        """Prepare values for child_ids"""
        vals = {
            "name": data.get("username")
            or data.get("first_name")
            and data.get("last_name")
            and f"{data.get('first_name')} {data.get('last_name')}"
            or data.get("first_name")
            or data.get("email"),
            "firstname": data.get("first_name") or data.get("email"),
            "lastname": data.get("last_name"),
            "email": data.get("email"),
            "type": address_type,
            "street": data.get("address_1"),
            "street2": data.get("address_2"),
            "zip": data.get("postcode"),
            "phone": data.get("phone"),
            "state_id": state.id if state else False,
        }
        return vals

    @mapping
    def child_ids(self, record):
        """Mapping for Invoice and Shipping Addresses"""
        billing = record.get("billing")
        shipping = record.get("shipping")
        child_data = []
        hash_to_partner = {}
        fields_to_check = ["first_name", "email"]
        for data, address_type in [(billing, "invoice"), (shipping, "delivery")]:
            if not any(data.get(field) for field in fields_to_check):
                continue
            if data.get("billing"):
                state = billing.get("state")
            else:
                state = shipping.get("state")
            if state:
                state = self.env["res.country.state"].search(
                    [("code", "=", state)],
                    limit=1,
                )
            hash_attributes = (
                data.get("username"),
                data.get("first_name"),
                data.get("last_name"),
                data.get("email"),
                data.get("address_1"),
                data.get("address_2"),
                address_type,
                data.get("postcode"),
                data.get("phone"),
            )
            hash_key = hashlib.md5(
                "|".join(str(attr) for attr in hash_attributes).encode()
            ).hexdigest()
            if hash_key in hash_to_partner:
                child_data.append(hash_to_partner[hash_key])
            else:
                existing_partner = self.env["res.partner"].search(
                    [("hash_key", "=", hash_key)], limit=1
                )
                if existing_partner:
                    hash_to_partner[hash_key] = existing_partner.id
                    child_data.append(existing_partner.id)
                else:
                    address_data = self._prepare_partner_vals(data, address_type, state)
                    address_data["hash_key"] = hash_key
                    address_data = self.env["res.partner"].create(address_data)
                    hash_to_partner[hash_key] = address_data.id
                    child_data.append(address_data.id)
        return {"child_ids": child_data} if child_data else {}

    @mapping
    def backend_id(self, record):
        """Return backend."""
        return {"backend_id": self.backend_record.id}


class WooResPartnerImporter(Component):
    """Importer the WooCommerce Partner"""

    _name = "woo.res.partner.importer"
    _inherit = "woo.importer"
    _apply_on = "woo.res.partner"
