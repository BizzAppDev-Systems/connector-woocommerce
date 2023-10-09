# import logging

from odoo import fields, models

from ...components.binder import WooModelBinder

# _logger = logging.getLogger(__name__)


class AccountTax(models.Model):
    _inherit = "account.tax"

    woo_bind_ids = fields.One2many(
        comodel_name="woo.account.tax",
        inverse_name="odoo_id",
        string="WooCommerce Bindings",
        copy=False,
    )


class WooAccountTax(models.Model):
    """Woocommerce Account Tax"""

    _name = "woo.account.tax"
    _inherit = "woo.binding"
    _inherits = {"account.tax": "odoo_id"}
    _description = "WooCommerce Account Tax"

    _rec_name = "name"

    odoo_id = fields.Many2one(
        comodel_name="account.tax",
        string="Account Tax",
        required=True,
        ondelete="restrict",
    )

    def __init__(self, name, bases, attrs):
        """Bind Odoo Account Tax"""
        WooModelBinder._apply_on.append(self._name)
        super(WooAccountTax, self).__init__(name, bases, attrs)
