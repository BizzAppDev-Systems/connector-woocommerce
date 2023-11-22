import logging
from collections import defaultdict

from odoo import api, fields, models

from odoo.addons.component.core import Component
from odoo.addons.component_event import skip_if

from ...components import utils

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = "product.product"

    woo_bind_ids = fields.One2many(
        comodel_name="woo.product.product",
        inverse_name="odoo_id",
        string="WooCommerce Bindings",
        copy=False,
    )
    stock_manage = fields.Boolean(compute="_compute_stock_manage", store=True)
    backend_stock_manage = fields.Boolean(
        compute="_compute_backend_stock_manage", store=True
    )

    def update_stock_qty(self):
        """
        Update the stock quantity for each binding in
        the WooCommerce integration.
        """
        for binding in self.woo_bind_ids:
            binding.recompute_woo_qty()

    @api.depends(
        "woo_bind_ids",
        "woo_bind_ids.stock_management",
    )
    def _compute_stock_manage(self):
        """Compute the stock management status for each WooCommerce Product."""
        for product in self:
            product.stock_manage = any(product.woo_bind_ids.mapped("stock_management"))

    @api.depends(
        "woo_bind_ids",
        "woo_bind_ids.backend_id.update_stock_inventory",
    )
    def _compute_backend_stock_manage(self):
        """Compute the value of backend_stock_manage for each product."""
        for product in self:
            product.backend_stock_manage = (
                self.woo_bind_ids.backend_id.update_stock_inventory
            )

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
    stock_management = fields.Boolean(readonly=True)
    woo_product_qty = fields.Float(
        string="Computed Quantity",
        help="""Last computed quantity to send " "on WooCommerce.""",
    )

    def recompute_woo_qty(self):
        """
        Check if the quantity in the stock location configured
        on the backend has changed since the last export.

        If it has changed, write the updated quantity on `woo_product_qty`.
        The write on `woo_product_qty` will trigger an `on_record_write`
        event that will create an export job.

        It groups the products by backend to avoid to read the backend
        informations for each product.
        """
        # group products by backend
        backends = defaultdict(lambda: self.env["woo.product.product"])
        for woo_product in self:
            backends[woo_product.backend_id] |= woo_product
        for backend, woo_products in backends.items():
            self._recompute_woo_qty_backend(backend, woo_products)
        return True

    def _recompute_woo_qty_backend(self, backend, products, read_fields=None):
        """
        Recompute the products quantity for one backend.

        If field names are passed in ``read_fields`` (as a list), they
        will be read in the product that is used in
        :meth:`~._woo_qty`.

        """
        if backend.product_stock_field_id:
            stock_field = backend.product_stock_field_id.name
        else:
            stock_field = "virtual_available"
        location = backend.warehouse_id.lot_stock_id
        product_fields = ["woo_product_qty", stock_field]
        if read_fields:
            product_fields += read_fields
        self_with_location = self.sudo().with_context(location=location.id)
        for chunk_ids in utils.chunks(products.ids, backend.recompute_qty_step):
            records = self_with_location.browse(chunk_ids)
            for product in records:
                new_qty = self._woo_qty(product, backend, location, stock_field)
                if not new_qty != product["woo_product_qty"]:
                    continue
                product.woo_product_qty = new_qty

    def _woo_qty(self, product, backend, location, stock_field):
        """
        Return the current quantity for one product.

        Can be inherited to change the way the quantity is computed,
        according to a backend / location.

        If you need to read additional fields on the product, see the
        ``read_fields`` argument of :meth:`~._recompute_woo_qty_backend`

        """
        return product[stock_field]


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


class WooBindingProductListener(Component):
    _name = "woo.binding.product.product.listener"
    _inherit = "base.connector.listener"
    _apply_on = ["woo.product.product", "woo.product.template"]

    # fields which should not trigger an export of the products
    # but an export of their inventory
    INVENTORY_FIELDS = (
        "stock_management",
        "woo_product_qty",
    )

    @skip_if(lambda self, record, *args, **kwargs: self.no_connector_export(record))
    def on_record_write(self, record, fields=None):
        """
        This method is triggered when a record of the 'woo.product.product' or
        'woo.product.template' models is written.
        It handles the export of product information or inventory updates based
        on the changed fields.
        """
        job_options = {}
        inventory_fields = list(set(fields).intersection(self.INVENTORY_FIELDS))
        if inventory_fields:
            if "description" not in job_options:
                description = record.export_record.__doc__
                job_options[
                    "description"
                ] = record.backend_id.get_queue_job_description(
                    description, record._description
                )
            job_options["priority"] = 20
            record.with_delay(**job_options or {}).export_record(
                backend=record.backend_id, record=record, fields=inventory_fields
            )
