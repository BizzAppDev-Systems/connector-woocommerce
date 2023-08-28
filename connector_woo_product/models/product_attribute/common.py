import logging

from odoo import fields, models, _
from odoo.exceptions import ValidationError
from odoo.addons.component.core import Component
from odoo.addons.connector_woo_base.components.binder import WooModelBinder

_logger = logging.getLogger(__name__)


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    woo_bind_ids = fields.One2many(
        comodel_name="woo.product.attribute",
        inverse_name="odoo_id",
        string="WooCommerce Bindings",
        copy=False,
    )
    woo_backend_id = fields.Many2one(
        comodel_name="woo.backend",
        string="WooCommerce Backend",
        ondelete="restrict",
    )
    has_archives = fields.Boolean()

    def import_product_attribute_value(self):
        """Import Product Attribute Value of account move."""
        self.ensure_one()
        if not self.woo_backend_id:
            raise ValidationError(_("Please add backend on Product Attribute."))
        filters = {
            "per_page": self.woo_backend_id.default_limit,
            "page": 1,
            "attribute": self.woo_bind_ids[0].external_id,
        }
        self.env["woo.product.attribute.value"].with_delay(priority=5).import_batch(
            self.woo_backend_id, filters=filters
        )


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

    def __init__(self, name, bases, attrs):
        """Bind Odoo Product Attribute"""
        WooModelBinder._apply_on.append(self._name)
        super(WooProductAttribute, self).__init__(name, bases, attrs)


class WooProductAttributeAdapter(Component):
    """Adapter for WooCommerce Product Attribute"""

    _name = "woo.product.attribute.adapter"
    _inherit = "woo.adapter"
    _apply_on = "woo.product.attribute"
    _woo_model = "products/attributes"
    _odoo_ext_id_key = "id"
