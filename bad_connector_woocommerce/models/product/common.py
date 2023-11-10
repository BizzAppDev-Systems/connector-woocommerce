import logging

from odoo import fields, models

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = "product.product"

    woo_bind_ids = fields.One2many(
        comodel_name="woo.product.product",
        inverse_name="odoo_id",
        string="WooCommerce Bindings",
        copy=False,
    )

    # @api.depends("product_template_attribute_value_ids")
    # def _compute_combination_indices(self):
    #     """
    #     Override method since we are not using attributes and attribute
    #     values for storing variant data we have to disable the combination check
    #     """
    #     for product in self:
    #         product.combination_indices = str(product.id)

    def _get_attribute_id_format(self, attribute, record, option=None):
        """Return the attribute and attribute value's unique id"""
        if not option:
            return "{}-{}".format(attribute.get("name"), record.get("id"))
        return "{}-{}-{}".format(option, attribute.get("id"), record.get("id"))

    def _get_product_attribute(self, attribute_id, record, env):
        """Get the product attribute that contains id as zero"""
        binder = env.binder_for("woo.product.attribute")
        created_id = self._get_attribute_id_format(attribute_id, record)
        product_attribute = binder.to_internal(created_id)
        if not product_attribute and not attribute_id.get("id"):
            product_attribute = self.env["woo.product.attribute"].create(
                {
                    "name": attribute_id.get("name"),
                    "backend_id": env.backend_record.id,
                    "external_id": created_id,
                    "not_real": True,
                }
            )
        return product_attribute

    def _create_attribute_values(
        self, options, product_attribute, attribute, record, env
    ):
        """Create attribute value binding that doesn't contain ids"""
        binder = env.binder_for("woo.product.attribute.value")
        for option in options:
            created_id = self._get_attribute_id_format(attribute, record, option)
            product_attribute_value = binder.to_internal(created_id)
            if not product_attribute_value:
                attribute_id = self._get_attribute_id_format(attribute, record)
                binder = env.binder_for("woo.product.attribute")
                product_attr = binder.to_internal(attribute_id, unwrap=True)
                attribute_value = self.env["product.attribute.value"].search(
                    [
                        ("name", "=", option),
                        ("attribute_id", "=", product_attr.id),
                    ],
                    limit=1,
                )
                self.env["woo.product.attribute.value"].create(
                    {
                        "name": option,
                        "attribute_id": product_attribute.odoo_id.id,
                        "woo_attribute_id": product_attribute.id,
                        "backend_id": env.backend_record.id,
                        "external_id": created_id,
                        "odoo_id": attribute_value.id if attribute_value else None,
                    }
                )
        return True


class WooProductProduct(models.Model):
    """Woocommerce Product Product"""

    _name = "woo.product.product"
    _inherit = "woo.binding"
    _inherits = {"product.product": "odoo_id"}
    _description = "WooCommerce Product"

    _rec_name = "name"

    woo_product_name = fields.Char(string="WooCommerce Product Name")
    odoo_id = fields.Many2one(
        comodel_name="product.product",
        string="Odoo Product",
        required=True,
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
    price = fields.Char()
    regular_price = fields.Char()
    woo_product_image_url_ids = fields.Many2many(
        comodel_name="woo.product.image.url",
        string="WooCommerce Product Image URL",
        ondelete="restrict",
    )


class WooProductProductAdapter(Component):
    """Adapter for WooCommerce Product Product"""

    _name = "woo.product.product.adapter"
    _inherit = "woo.adapter"
    _apply_on = "woo.product.product"
    _woo_model = "products"
    _woo_product_variation = "products/{product_id}"
    _woo_ext_id_key = "id"
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
        (
            "woo.product.template",
            "parent_id",
        ),
    }

    def search(self, filters=None, **kwargs):
        """Inherited search method to pass different API
        to fetch additional data"""
        kwargs["_woo_product_variation"] = self._woo_product_variation
        return super(WooProductProductAdapter, self).search(filters, **kwargs)
