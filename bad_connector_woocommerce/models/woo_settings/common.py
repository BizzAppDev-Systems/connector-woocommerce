import logging

from odoo import fields, models

from odoo.addons.component.core import Component

from ...components.binder import WooModelBinder

_logger = logging.getLogger(__name__)


class WooSettings(models.Model):
    _name = "woo.settings"
    _description = "WooCommerce Settings"
    _inherit = "woo.binding"

    name = fields.Char(required=True)
    woo_type = fields.Char()
    default = fields.Char()
    tip = fields.Char()
    value = fields.Char()
    options = fields.Char()
    description = fields.Char()
    odoo_id = fields.Many2one(
        string="WooCommerce Settings", comodel_name="woo.settings"
    )

    def __init__(self, name, bases, attrs):
        """Bind Odoo WooCommerce Settings"""
        WooModelBinder._apply_on.append(self._name)
        super(WooSettings, self).__init__(name, bases, attrs)


class WooSettingsAdapter(Component):
    """Adapter for WooCommerce Settings"""

    _name = "woo.setting.adapter"
    _inherit = "woo.adapter"
    _apply_on = "woo.settings"
    _woo_model = "settings/tax"
    _woo_ext_id_key = "id"
