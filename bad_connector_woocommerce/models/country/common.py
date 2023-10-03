from odoo import models
from odoo import fields, models
# from ...components.binder import WooModelBinder
from odoo.addons.component.core import Component


class ResCountry(models.Model):
    _inherit = "res.country"


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

    # def __init__(self, name, bases, attrs):
    #     """Bind Odoo Country"""
    #     WooModelBinder._apply_on.append(self._name)
    #     super(WooResCountry, self).__init__(name, bases, attrs)


class WooResCountryAdapter(Component):
    """Adapter for WooCommerce Res Partner"""

    _name = "woo.res.country.adapter"
    _inherit = "woo.adapter"
    _apply_on = "woo.res.country"
    _woo_model = "data/countries"
    _odoo_ext_id_key = "id"
