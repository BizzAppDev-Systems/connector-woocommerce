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
        string="Woo Bindings",
        copy=False,
    )
    woo_backend_id = fields.Many2one(
        comodel_name="woo.backend",
        string="Woo Backend",
        ondelete="restrict",
    )
    woo_id = fields.Char()
    woo_attribute_id = fields.Many2one(
        comodel_name="woo.product.attribute",
        string="Woo Product Attribute",
        ondelete="restrict",
    )


class WooProductAttributeValue(models.Model):
    """Woocommerce product attribute value"""

    _name = "woo.product.attribute.value"
    _inherit = "woo.binding"
    _inherits = {"product.attribute.value": "odoo_id"}
    _description = "Woo Product Attribute Value"

    _rec_name = "name"

    odoo_id = fields.Many2one(
        comodel_name="product.attribute.value",
        string="Product",
        required=True,
        ondelete="restrict",
    )

    def __init__(self, *args, **kwargs):
        """Bind Woo Product Attribute Value"""
        super().__init__(*args, **kwargs)
        WooModelBinder._apply_on.append(self._name)


class WooProductAttributeValueAdapter(Component):
    """Adapter for WooCommerce Product Attribute Value"""

    _name = "woo.product.attribute.value.adapter"
    _inherit = "woo.adapter"
    _apply_on = "woo.product.attribute.value"
    _woo_model = "products/attributes"
    _woo_key = "id"
    _odoo_ext_id_key = "id"

    def search_read(self, filters=None, **kwargs):
        """Method to get the records from woo"""
        resource_path = "{}/{}/terms".format(self._woo_model, filters.get("attribute"))
        result = self._call(
            resource_path=resource_path, arguments=filters, http_method="get"
        )
        result_lst = []
        for res in result:
            new_res = res.copy()
            new_res["attribute"] = filters.get("attribute")
            result_lst.append(new_res)
        return result_lst
