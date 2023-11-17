import logging

from odoo import api, fields, models

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

    variant_different = fields.Boolean()
    stock_manage_template = fields.Boolean(
        compute="_compute_stock_manage_template", store=True
    )
    backend_stock_manage = fields.Boolean(
        compute="_compute_backend_stock_manage", store=True
    )

    @api.depends(
        "woo_bind_ids",
        "woo_bind_ids.stock_management",
    )
    def _compute_stock_manage_template(self):
        """Compute the stock management status for each WooCommerce Product."""
        for template in self:
            template.stock_manage_template = any(
                template.woo_bind_ids.mapped("stock_management")
            )

    @api.depends(
        "woo_bind_ids",
        "woo_bind_ids.backend_id.update_stock_inventory",
    )
    def _compute_backend_stock_manage(self):
        for template in self:
            template.backend_stock_manage = (
                self.woo_bind_ids.backend_id.update_stock_inventory
            )

    def update_stock_qty(self):
        """
        Update the stock quantity for template in
        the WooCommerce integration.
        """
        for binding in self.woo_bind_ids:
            binding.update_woo_product_qty()


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
    woo_product_attribute_value_ids = fields.Many2many(
        comodel_name="woo.product.attribute.value",
        string="WooCommerce Product Attribute Value",
        ondelete="restrict",
    )
    stock_management = fields.Boolean(readonly=True)
    woo_product_qty = fields.Float(
        string="Computed Quantity",
        help="""Last computed quantity to send " "on WooCommerce.""",
    )

    def update_woo_product_qty(self):
        """
        Update woo_product_qty with the total on-hand variant quantities
        for products with stock_management set to true.
        """
        variants_with_stock_management = self.product_variant_ids.filtered(
            lambda variant: variant.woo_bind_ids.filtered("stock_management")
        )
        total_qty = sum(variants_with_stock_management.mapped("qty_available"))
        self.write({"woo_product_qty": total_qty})


class WooProductTemplateAdapter(Component):
    """Adapter for WooCommerce Product Template"""

    _name = "woo.product.template.adapter"
    _inherit = "woo.adapter"
    _apply_on = "woo.product.template"
    _woo_model = "products"
    _woo_ext_id_key = "id"
    _model_dependencies = {
        (
            "woo.product.attribute",
            "attributes",
        ),
    }
