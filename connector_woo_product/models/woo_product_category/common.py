import logging

from odoo import fields, models

from odoo.addons.component.core import Component
from odoo.addons.connector_woo_base.components.binder import WooModelBinder

_logger = logging.getLogger(__name__)


class WooProductCategory(models.Model):
    _name = "woo.product.category"
    _description = "Woo Product Category"
    _parent_name = "parent_id"
    _parent_store = True

    name = fields.Char()
    slug = fields.Char()
    display = fields.Char()
    menu_order = fields.Integer()
    count = fields.Integer(readonly=True)
    parent_path = fields.Char(index=True, unaccent=False)
    parent_id = fields.Many2one(
        comodel_name="woo.product.category",
        string="Parent Category",
        index=True,
        ondelete="cascade",
    )
    description = fields.Html(string="Description", translate=True)
    odoo_id = fields.Many2one(
        string="Product Category",
    )

    woo_bind_ids = fields.One2many(
        comodel_name="woocommerce.product.category",
        inverse_name="odoo_id",
        string="Woo Bindings",
        copy=False,
    )
    woo_backend_id = fields.Many2one(
        comodel_name="woo.backend",
        string="Woo Backend",
        ondelete="restrict",
    )


class WooCommerceProductCategory(models.Model):
    """Woocommerce product Category"""

    _name = "woocommerce.product.category"
    _inherit = "woo.binding"
    _inherits = {"woo.product.category": "odoo_id"}
    _description = "WooCommerce Product Category"

    _rec_name = "name"

    odoo_id = fields.Many2one(
        comodel_name="woo.product.category",
        string=" WooCommerce Product Category",
        required=True,
        ondelete="restrict",
    )
    woo_parent_id = fields.Many2one(
        comodel_name="woocommerce.product.category",
        string="Woo Parent Category",
        ondelete="cascade",
    )
    woo_child_ids = fields.One2many(
        comodel_name="woocommerce.product.category",
        inverse_name="woo_parent_id",
        string="WooCommerce Child Categories",
    )
    woo_id = fields.Char()

    def __init__(self, *args, **kwargs):
        """Bind Odoo Product Category"""
        super().__init__(*args, **kwargs)
        WooModelBinder._apply_on.append(self._name)


class WooProductCategoryAdapter(Component):
    """Adapter for WooCommerce Product Category"""

    _name = "woo.product.category.adapter"
    _inherit = "woo.adapter"
    _apply_on = "woocommerce.product.category"
    _woo_model = "products/categories"
    _odoo_ext_id_key = "id"
