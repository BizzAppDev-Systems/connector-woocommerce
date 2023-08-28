import logging

from odoo import fields, models

from odoo.addons.component.core import Component
from odoo.addons.connector_woo_base.components.binder import WooModelBinder

_logger = logging.getLogger(__name__)


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    description = fields.Html(string="Description", translate=True)
    woo_bind_ids = fields.One2many(
        comodel_name="woo.product.attribute.value",
        inverse_name="odoo_id",
        string="WooCommerce Bindings",
        copy=False,
    )
    woo_backend_id = fields.Many2one(
        comodel_name="woo.backend",
        string="WooCommerce Backend",
        ondelete="restrict",
    )
    woo_attribute_id = fields.Many2one(
        comodel_name="woo.product.attribute",
        string="WooCommerce Product Attribute",
        ondelete="restrict",
    )
    woo_product_template_variant_value_ids = fields.Many2many(
        comodel_name="woo.product.attribute.value",
        string="WooCommerce Product Template Variant Value",
        ondelete="restrict",
    )


class WooProductAttributeValue(models.Model):
    """Woocommerce product attribute value"""

    _name = "woo.product.attribute.value"
    _inherit = "woo.binding"
    _inherits = {"product.attribute.value": "odoo_id"}
    _description = "WooCommerce Product Attribute Value"

    _rec_name = "name"

    odoo_id = fields.Many2one(
        comodel_name="product.attribute.value",
        string="Product Attribute Value",
        required=True,
        ondelete="restrict",
    )

    def __init__(self, name, bases, attrs):
        """Bind Odoo Product Attribute Value"""
        WooModelBinder._apply_on.append(self._name)
        super(WooProductAttributeValue, self).__init__(name, bases, attrs)


class WooProductAttributeValueAdapter(Component):
    """Adapter for WooCommerce Product Attribute Value"""

    _name = "woo.product.attribute.value.adapter"
    _inherit = "woo.adapter"
    _apply_on = "woo.product.attribute.value"
    _woo_model = "products/attributes"
    _odoo_ext_id_key = "id"

    def search(self, filters=None, **kwargs):
        """Method to get the records from woo"""
        resource_path = "{}/{}/terms".format(self._woo_model, filters.get("attribute"))
        result = self._call(
            resource_path=resource_path, arguments=filters, http_method="get"
        )
        result_lst = []
        for res in result:
            res["attribute"] = filters.get("attribute")
            result_lst.append(res)
        return result_lst