import logging

from odoo import api, fields, models

from odoo.addons.component.core import Component
from odoo.addons.connector_woo_base.components.binder import WooModelBinder

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    woo_bind_ids = fields.One2many(
        comodel_name="woo.res.partner",
        inverse_name="odoo_id",
        string="Woo Bindings",
        copy=False,
    )
    firstname = fields.Char(string="First Name")
    lastname = fields.Char(string="Last Name")
    # Inherited the field to add store true and compute for add first and last name
    name = fields.Char(compute="_compute_name", store=True, readonly=False)

    @api.depends("firstname", "lastname")
    def _compute_name(self):
        """
        Update the 'name' field based on 'firstname' and 'lastname' values.
        If both 'firstname' and 'lastname' exist, set 'name' as a combination
        of both. If only 'firstname' exists, set 'name' to 'firstname'. If only
        'lastname' exists, set 'name' to 'lastname'. If neither 'firstname'
        nor 'lastname' exists, set 'name' to an empty string.
        """
        for partner in self:
            if partner.firstname and partner.lastname:
                partner.name = f"{partner.firstname} {partner.lastname}"
            elif partner.firstname:
                partner.name = partner.firstname
            elif partner.lastname:
                partner.name = partner.lastname
            else:
                partner.name = ""


class WooResPartner(models.Model):
    _name = "woo.res.partner"
    _inherit = "woo.binding"
    _inherits = {"res.partner": "odoo_id"}
    _description = "Woo Partner"

    _rec_name = "name"

    odoo_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        required=True,
        ondelete="restrict",
    )

    def __init__(self, *args, **kwargs):
        """Bind Odoo Partner"""
        super().__init__(*args, **kwargs)
        WooModelBinder._apply_on.append(self._name)


class WooResPartnerAdapter(Component):
    """Adapter for WooCommerce Res Partner"""

    _name = "woo.res.partner.adapter"
    _inherit = "woo.adapter"
    _apply_on = "woo.res.partner"

    _woo_model = "customers"
    _odoo_ext_id_key = "id"
