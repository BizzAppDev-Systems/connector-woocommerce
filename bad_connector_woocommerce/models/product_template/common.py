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

    variant_different = fields.Boolean()
    default_code = fields.Char(compute=False, inverse=False)
    backend_id = fields.Many2one(
        comodel_name="woo.backend",
        string="WooCommerce Backend",
        ondelete="restrict",
    )
    manage_stock_in_woocommerce = fields.Boolean(string="Manage Stock In WooCommerce ?")

    def product_template_export(self):
        """Export product template to Woocommerce"""
        model = self.env["woo.product.template"]
        job_options = {}
        if not self.backend_id:
            raise ValidationError(
                _(
                    "WooCommerce Backend is not set in Product %s."
                    "Please set WooCommerce Backend"
                )
                % (self.name)
            )
        description = self.backend_id.get_queue_job_description(
            prefix=model.export_record.__doc__ or "Record Export To",
            model=model._description,
        )
        job_options["description"] = description
        delayable = model.with_delay(**job_options or {})
        delayable.export_record(backend=self.backend_id, record=self)


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
    woo_product_categ_ids = fields.Many2many(
        comodel_name="woo.product.category",
        string="WooCommerce Product Category(Product)",
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


class WooProductTemplateAdapter(Component):
    """Adapter for WooCommerce Product Template"""

    _name = "woo.product.template.adapter"
    _inherit = "woo.adapter"
    _apply_on = "woo.product.template"
    _woo_model = "products"
    _woo_ext_id_key = "id"
    _check_import_sync_date = True
    _model_dependencies = {
        (
            "woo.product.category",
            "categories",
        ),
        (
            "woo.product.attribute",
            "attributes",
        ),
        (
            "woo.product.tag",
            "tags",
        ),
    }
