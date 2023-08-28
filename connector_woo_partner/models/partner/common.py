import logging
import hashlib
from odoo import fields, models
from odoo.addons.component.core import Component
from odoo.addons.connector_woo_base.components.binder import WooModelBinder

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    woo_bind_ids = fields.One2many(
        comodel_name="woo.res.partner",
        inverse_name="odoo_id",
        string="WooCommerce Bindings",
        copy=False,
    )
    firstname = fields.Char(string="First Name")
    lastname = fields.Char(string="Last Name")
    hash_key = fields.Char(string="Hash Key")

    def _prepare_child_partner_vals(self, data, address_type, state):
        """Prepare values for child_ids"""
        vals = {
            "name": data.get("username")
            or data.get("first_name")
            and data.get("last_name")
            and f"{data.get('first_name')} {data.get('last_name')}"
            or data.get("first_name")
            or data.get("email"),
            "firstname": data.get("first_name"),
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

    def _process_address_data(self, data, address_type, state):
        """
        Process address data, generate hash key, and handle partner creation or retrieval.
        """
        state_obj = None
        if state:
            state_obj = self.env["res.country.state"].search(
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
        existing_partner = self.env["res.partner"].search(
            [("hash_key", "=", hash_key)], limit=1
        )
        if not existing_partner:
            address_data = self._prepare_child_partner_vals(
                data, address_type, state_obj
            )
            address_data["hash_key"] = hash_key
            partner_id = self.env["res.partner"].create(address_data)
            return partner_id.id
        return existing_partner.id

    def child(self, record):
        """Mapping for Invoice and Shipping Addresses"""
        billing = record.get("billing")
        shipping = record.get("shipping")
        child_data = []
        fields_to_check = ["first_name", "email"]

        for data, address_type in [(billing, "invoice"), (shipping, "delivery")]:
            if not any(data.get(field) for field in fields_to_check):
                continue
            state = (
                billing.get("state") if data.get("billing") else shipping.get("state")
            )
            partner_id = self._process_address_data(data, address_type, state)
            child_data.append(partner_id)
        return child_data


class WooResPartner(models.Model):
    _name = "woo.res.partner"
    _inherit = "woo.binding"
    _inherits = {"res.partner": "odoo_id"}
    _description = "WooCommerce Partner"

    _rec_name = "name"

    odoo_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        required=True,
        ondelete="restrict",
    )

    def __init__(self, name, bases, attrs):
        """Bind Odoo Partner"""
        WooModelBinder._apply_on.append(self._name)
        super(WooResPartner, self).__init__(name, bases, attrs)


class WooResPartnerAdapter(Component):
    """Adapter for WooCommerce Res Partner"""

    _name = "woo.res.partner.adapter"
    _inherit = "woo.adapter"
    _apply_on = "woo.res.partner"
    _woo_model = "customers"
    _odoo_ext_id_key = "id"
