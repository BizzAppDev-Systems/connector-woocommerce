import logging

from odoo import fields, models

from odoo.addons.component.core import Component

from ...components.binder import WooModelBinder

_logger = logging.getLogger(__name__)


class ProductTag(models.Model):
    _inherit = "product.tag"

    woo_bind_ids = fields.One2many(
        comodel_name="woo.product.tag",
        inverse_name="odoo_id",
        string="WooCommerce Bindings",
        copy=False,
    )


class WooProductTag(models.Model):
    """Woocommerce product tag"""

    _name = "woo.product.tag"
    _inherit = "woo.binding"
    _inherits = {"product.tag": "odoo_id"}
    _description = "WooCommerce Product Tag"

    _rec_name = "name"

    odoo_id = fields.Many2one(
        comodel_name="product.tag",
        string="Product Tag",
        required=True,
        ondelete="restrict",
    )

    def __init__(self, name, bases, attrs):
        """Bind Odoo Product Tag"""
        WooModelBinder._apply_on.append(self._name)
        super(WooProductTag, self).__init__(name, bases, attrs)


class WooProductTagAdapter(Component):
    """Adapter for WooCommerce Product Attribute"""

    _name = "woo.product.tag.adapter"
    _inherit = "woo.adapter"
    _apply_on = "woo.product.tag"
    _woo_model = "products/tags"
    _woo_ext_id_key = "id"
