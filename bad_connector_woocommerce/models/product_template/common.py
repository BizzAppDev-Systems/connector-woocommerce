import logging

from odoo import _, fields, models
from odoo.exceptions import ValidationError

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

    woo_attribute_ids = fields.Many2many(
        comodel_name="woo.product.attribute",
        string="WooCommerce Product Attribute",
        ondelete="restrict",
    )
    woo_product_categ_ids = fields.Many2many(
        comodel_name="woo.product.category",
        string="WooCommerce Product Category(Product)",
        ondelete="restrict",
    )
    woo_product_attribute_value_ids = fields.Many2many(
        comodel_name="woo.product.attribute.value",
        string="WooCommerce Product Attribute Value",
        ondelete="restrict",
    )
    woo_product_image_url_ids = fields.Many2many(
        comodel_name="woo.product.image.url",
        string="WooCommerce Product Image URL",
        ondelete="restrict",
    )

    def sync_product_variants_from_woo(self):
        """sync Attribute values from woocommerce"""
        self.ensure_one()
        filters = {}
        if not self.backend_id:
            raise ValidationError(_("No Backend found on Product Template."))
        if not self.external_id:
            raise ValidationError(_("No External Id found in backend"))
        filters.update(
            {
                "product_template": self.external_id,
            }
        )
        # TODO: with_delay only if context has delay key passed from after import. Else
        # it should be without delay
        self.backend_id._sync_from_date(
            model="woo.product.product",
            priority=5,
            filters=filters,
        )


class WooProductTemplateAdapter(Component):
    """Adapter for WooCommerce Product Template"""

    _name = "woo.product.template.adapter"
    _inherit = "woo.adapter"
    _apply_on = "woo.product.template"
    _woo_model = "products"
    _woo_ext_id_key = "id"
