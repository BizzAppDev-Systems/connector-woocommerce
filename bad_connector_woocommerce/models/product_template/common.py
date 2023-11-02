import logging

from odoo import fields, models

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    woo_bind_ids = fields.One2many(
        comodel_name="woo.product.template",
        inverse_name="odoo_id",
        string="WooCommerce Bindings",
        copy=False,
    )


class WooProductTemplate(models.Model):
    """Woocommerce Product Template"""

    _name = "woo.product.template"
    _inherit = "woo.binding"
    _inherits = {"product.template": "odoo_id"}
    _description = "WooCommerce Product Template"
    _rec_name = "name"

    odoo_id = fields.Many2one(
        comodel_name="product.template",
        string="Odoo Product Template",
        required=True,
        ondelete="restrict",
    )


class WooProductTemplateAdapter(Component):
    """Adapter for WooCommerce Product Template"""

    _name = "woo.product.template.adapter"
    _inherit = "woo.adapter"
    _apply_on = "woo.product.template"
    _woo_model = "products"
    _woo_ext_id_key = "id"
