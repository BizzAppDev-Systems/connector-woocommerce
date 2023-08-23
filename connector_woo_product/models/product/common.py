import logging

from odoo import fields, models

from odoo.addons.component.core import Component
from odoo.addons.connector_woo_base.components.binder import WooModelBinder

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = "product.product"

    woo_bind_ids = fields.One2many(
        comodel_name="woo.product.product",
        inverse_name="odoo_id",
        string="Woo Bindings",
        copy=False,
    )
    woo_backend_id = fields.Many2one(
        comodel_name="woo.backend",
        string="Woo Backend",
        ondelete="restrict",
    )
    status = fields.Selection(
        [
            ("any", "Any"),
            ("draft", "Draft"),
            ("pending", "Pending"),
            ("private", "Private"),
            ("publish", "Publish"),
        ],
        string="Status",
        default="any",
    )
    tax_status = fields.Selection(
        [
            ("taxable", "Taxable"),
            ("shipping", "Shipping"),
            ("none", "None"),
        ],
        string="Tax Status",
        default="taxable",
    )
    stock_status = fields.Selection(
        [
            ("instock", "Instock"),
            ("outofstock", "Out Of Stock"),
            ("onbackorder", "On Backorder"),
        ],
        string="Stock Status",
        default="instock",
    )
    woo_attribute_ids = fields.Many2many(
        comodel_name="woo.product.attribute",
        string="Woo Product Attribute",
        ondelete="restrict",
    )
    woo_product_categ_ids = fields.Many2many(
        comodel_name="woo.product.category",
        string="WooCommerce Product Category",
        ondelete="restrict",
    )
    woo_product_template_variant_value_ids = fields.Many2many(
        comodel_name="woo.product.attribute.value",
        string="WooCommerce Product Template Variant Value",
        ondelete="restrict",
    )


class WooProductProduct(models.Model):
    """Woocommerce product product"""

    _name = "woo.product.product"
    _inherit = "woo.binding"
    _inherits = {"product.product": "odoo_id"}
    _description = "Woo Product"

    _rec_name = "name"

    odoo_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        required=True,
        ondelete="restrict",
    )
    woocommerce_product_category_ids = fields.Many2many(
        comodel_name="woo.product.category",
        string="Woo Product Attribute",
        ondelete="restrict",
    )

    def __init__(self, *args, **kwargs):
        """Bind Woo Product"""
        super().__init__(*args, **kwargs)
        WooModelBinder._apply_on.append(self._name)


class WooProductProductAdapter(Component):
    """Adapter for WooCommerce Product Product"""

    _name = "woo.product.product.adapter"
    _inherit = "woo.adapter"
    _apply_on = "woo.product.product"
    _woo_model = "products"
    _odoo_ext_id_key = "id"
    _model_dependencies = [
        (
            "woocommerce.product.category",
            "woo.product.attribute",
        ),
    ]
