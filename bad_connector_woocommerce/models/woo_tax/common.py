import logging

from odoo import fields, models

from odoo.addons.component.core import Component

from ...components.binder import WooModelBinder

_logger = logging.getLogger(__name__)


class WooTax(models.Model):
    _name = "woo.tax"
    _inherit = "woo.binding"
    _description = "WooCommerce Taxes"

    name = fields.Char(required=True)
    woo_amount = fields.Float()
    woo_rate = fields.Char()
    woo_tax_name = fields.Char(string="WooCommerce Tax Name")
    priority = fields.Char()
    shipping = fields.Char()
    woo_class = fields.Char()
    compound = fields.Char()
    state = fields.Char()
    city = fields.Char()
    cities = fields.Char()
    postcode = fields.Char()
    postcodes = fields.Char()
    company_id = fields.Many2one(comodel_name="res.company", string="Company")
    tax_id = fields.Many2one(
        string="Related Tax",
        comodel_name="account.tax",
    )
    country_id = fields.Many2one(
        string="Country",
        comodel_name="res.country",
    )
    state_id = fields.Many2one(
        string="State",
        comodel_name="res.country.state",
    )
    woo_bind_ids = fields.One2many(
        comodel_name="woo.tax",
        inverse_name="odoo_id",
        string="WooCommerce Bindings",
        copy=False,
    )
    odoo_id = fields.Many2one(string="Taxes", comodel_name="account.tax")

    def __init__(self, name, bases, attrs):
        """Bind Odoo WooCommerce Taxes"""
        WooModelBinder._apply_on.append(self._name)
        super(WooTax, self).__init__(name, bases, attrs)


class WooTaxAdapter(Component):
    """Adapter for WooCommerce Tax"""

    _name = "woo.tax.adapter"
    _inherit = "woo.adapter"
    _apply_on = "woo.tax"
    _woo_model = "taxes"
    _woo_ext_id_key = "id"
