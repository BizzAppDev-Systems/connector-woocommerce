import hashlib
import logging

from odoo import _, fields, models

from odoo.addons.component.core import Component
from odoo.addons.connector.exception import MappingError
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

    def write(self, vals):
        if set(vals.keys()) & {
            "firstname",
            "lastname",
            "email",
            "mobile",
            "phone",
            "street",
            "street2",
            "city",
            "state_id",
            "zip",
            "country_id",
        }:
            vals["hash_key"] = False

        return super(ResPartner, self).write(vals)

    def _prepare_child_partner_vals(self, data, address_type=None):
        """Prepare values for child_ids"""
        country = data.get("country")
        state = data.get("state")
        if "-" in state:
            state = state.split("-")[0]
        country = self.env["res.country"].search(
            [("code", "=ilike", country)],
            limit=1,
        )
        state = self.env["res.country.state"].search(
            [("code", "=ilike", state)],
            limit=1,
        )
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
            "type": address_type or "",
            "street": data.get("address_1"),
            "street2": data.get("address_2"),
            "zip": data.get("postcode"),
            "phone": data.get("phone"),
            "state_id": state.id if state else False,
            "country_id": country.id if country else False,
            "city": data.get("city"),
        }
        return vals

    def _process_address_data(self, data, address_type, partner_ext_id, backend_id):
        """
        Process address data, generate hash key, and handle partner creation or retrieval.
        """
        hash_attributes = (
            data.get("username"),
            data.get("first_name"),
            data.get("last_name"),
            data.get("email"),
            data.get("address_1"),
            data.get("address_2"),
            data.get("city"),
            data.get("country"),
            address_type,
            data.get("postcode"),
            data.get("phone"),
            partner_ext_id,
            backend_id,
        )
        hash_key = hashlib.md5(
            "|".join(str(attr) for attr in hash_attributes).encode()
        ).hexdigest()
        existing_partner = self.env["res.partner"].search(
            [("hash_key", "=", hash_key)], limit=1
        )
        if existing_partner:
            return
        address_data = self._prepare_child_partner_vals(data, address_type)
        address_data["hash_key"] = hash_key
        return address_data

    def create_get_children(self, record, partner_ext_id, backend_id):
        """Mapping for Invoice and Shipping Addresses"""
        billing = record.get("billing")
        shipping = record.get("shipping")
        child_data = []
        for data, address_type in [(billing, "invoice"), (shipping, "delivery")]:
            if not any(data.values()):
                continue
            if (
                not data.get("email")
                and not backend_id.without_email
                and address_type != "delivery"
            ):
                raise MappingError(_("Email is Missing!"))
            address_data = self._process_address_data(
                data, address_type, partner_ext_id, backend_id
            )
            if not address_data:
                continue
            child_data.append(address_data)
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
