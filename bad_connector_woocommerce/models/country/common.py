from odoo import api, fields, models

from odoo.addons.component.core import Component

from ...components.binder import WooModelBinder


class ResCountry(models.Model):
    _inherit = "res.country"

    woo_bind_ids = fields.One2many(
        comodel_name="woo.res.country",
        inverse_name="odoo_id",
        string="WooCommerce Bindings",
        copy=False,
    )


class WooResCountry(models.Model):
    _name = "woo.res.country"
    _inherit = "woo.binding"
    _inherits = {"res.country": "odoo_id"}
    _description = "WooCommerce Country"

    odoo_id = fields.Many2one(
        comodel_name="res.country",
        string="Partner",
        required=True,
        ondelete="restrict",
    )
    woo_state_line_ids = fields.One2many(
        comodel_name="woo.res.country.state",
        inverse_name="woo_country_id",
        string="WooCommerce State Lines",
        copy=False,
    )
    woo_country_id = fields.Integer(
        string="WooCommerce Country ID", help="'country_id' field in WooCommerce"
    )

    def __init__(self, name, bases, attrs):
        """Bind Odoo Country"""
        WooModelBinder._apply_on.append(self._name)
        super(WooResCountry, self).__init__(name, bases, attrs)


class WooResCountryAdapter(Component):
    """Adapter for WooCommerce Res Partner"""

    _name = "woo.res.country.adapter"
    _inherit = "woo.adapter"
    _apply_on = "woo.res.country"
    _woo_model = "data/countries"
    _woo_ext_id_key = "code"
    # _odoo_ext_id_key = "code"


class WooResCountryState(models.Model):
    _name = "woo.res.country.state"
    _inherit = "woo.binding"
    _description = "WooCommerce Res Country State"
    _inherits = {"res.country.state": "odoo_id"}

    woo_country_id = fields.Many2one(
        comodel_name="woo.res.country",
        string="WooCommerce Country",
        required=True,
        ondelete="cascade",
        index=True,
    )
    odoo_id = fields.Many2one(
        comodel_name="res.country.state",
        string="Country State",
        required=True,
        ondelete="restrict",
    )

    def __init__(self, name, bases, attrs):
        """Bind Odoo Country State Line"""
        WooModelBinder._apply_on.append(self._name)
        super(WooResCountryState, self).__init__(name, bases, attrs)

    @api.model_create_multi
    def create(self, vals):
        for value in vals:
            record_country_state = self.env["res.country.state"].search(
                [
                    ("code", "=", value.get("code")),
                    ("name", "=", value.get("name")),
                ],
                limit=1,
            )
            existing_record = self.search(
                [
                    ("external_id", "=", value.get("external_id")),
                    ("backend_id", "=", value.get("backend_id")),
                ]
            )
            if not record_country_state and not existing_record:
                # if not existing_record:
                binding = self.env["woo.res.country"].browse(value["woo_country_id"])
                value["country_id"] = binding.odoo_id.id
        return super(WooResCountryState, self).create(vals)


class ResCountryState(models.Model):
    _inherit = "res.country.state"

    woo_bind_ids = fields.One2many(
        comodel_name="woo.res.country.state",
        inverse_name="odoo_id",
        string="WooCommerce Bindings(State Line)",
        copy=False,
    )
    woo_state_id = fields.Char()
