import logging

from odoo import fields, models

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class WooSettings(models.Model):
    _name = "woo.settings"
    _description = "WooCommerce Settings"
    _inherit = "woo.binding"

    name = fields.Char(required=True)
    woo_type = fields.Char()
    default = fields.Char()
    value = fields.Char()
    odoo_id = fields.Many2one(
        string="WooCommerce Settings", comodel_name="woo.settings"
    )


class WooSettingsAdapter(Component):
    """Adapter for WooCommerce Settings"""

    _name = "woo.setting.adapter"
    _inherit = "woo.adapter"
    _apply_on = "woo.settings"
    _remote_model = "settings/tax"
