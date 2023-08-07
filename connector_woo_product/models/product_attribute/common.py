import logging

from odoo import fields, models

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    woo_bind_ids = fields.One2many(
        comodel_name="woo.product.attribute",
        inverse_name="odoo_id",
        string="Woo Bindings",
        copy=False,
    )
    woo_backend_id = fields.Many2one(
        comodel_name="woo.backend",
        string="Woo Backend",
        ondelete="restrict",
    )
    woo_id = fields.Char()
    has_archives = fields.Boolean(default=False)


class WooProductAttribute(models.Model):
    """Woocommerce product attribute"""

    _name = "woo.product.attribute"
    _inherit = "woo.binding"
    _inherits = {"product.attribute": "odoo_id"}
    _description = "Woo Product Attribute"

    _rec_name = "name"

    odoo_id = fields.Many2one(
        comodel_name="product.attribute",
        string="Product Attribute",
        required=True,
        ondelete="restrict",
    )


class WooProductAttributeAdapter(Component):
    """Adapter for WooCommerce Product Attribute"""

    _name = "woo.product.attribute.adapter"
    _inherit = "woo.adapter"
    _apply_on = "woo.product.attribute"
    _woo_model = "products/attributes"
    _woo_key = "id"
    _odoo_ext_id_key = "woo_id"
