import logging

from odoo import fields, models

from odoo.addons.component.core import Component

from ...components.binder import WooModelBinder

_logger = logging.getLogger(__name__)


class WooTax(models.Model):
    _name = "woo.tax"
    _description = "WooCommerce Taxes"
    _inherit = "woo.binding"
    # _parent_name = "parent_id"
    # _parent_store = True

    name = fields.Char(required=True)
    woo_amount = fields.Float()
    woo_bind_ids = fields.One2many(
        comodel_name="woo.sale.order",
        inverse_name="odoo_id",
        string="WooCommerce Bindings",
        copy=False,
    )
    # display = fields.Char()
    # menu_order = fields.Integer()
    # count = fields.Integer(readonly=True)
    # parent_path = fields.Char(index=True, unaccent=False)
    # parent_id = fields.Many2one(
    #     comodel_name="woo.product.category",
    #     string="Parent Category",
    #     index=True,
    #     ondelete="cascade",
    # )
    # description = fields.Html(string="Description", translate=True)
    odoo_id = fields.Many2one(string="Taxes", comodel_name="woo.tax")
    # woo_parent_id = fields.Many2one(
    #     comodel_name="woo.product.category",
    #     string="WooCommerce Parent Category",
    #     ondelete="cascade",
    # )
    # woo_child_ids = fields.One2many(
    #     comodel_name="woo.product.category",
    #     inverse_name="woo_parent_id",
    #     string="WooCommerce Child Categories",
    # )

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
