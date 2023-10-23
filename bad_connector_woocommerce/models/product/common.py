import logging
from collections import defaultdict

from odoo import fields, models

from odoo.addons.component.core import Component
from odoo.addons.component_event import skip_if

_logger = logging.getLogger(__name__)


def chunks(items, length):
    for index in range(0, len(items), length):
        yield items[index : index + length]


class ProductProduct(models.Model):
    _inherit = "product.product"

    woo_bind_ids = fields.One2many(
        comodel_name="woo.product.product",
        inverse_name="odoo_id",
        string="WooCommerce Bindings",
        copy=False,
    )

    def update_stock_qty(self):
        """Import Product Attribute Value"""
        for binding in self.woo_bind_ids:
            binding.recompute_woo_qty()


class WooProductProduct(models.Model):
    """Woocommerce Product Product"""

    _name = "woo.product.product"
    _inherit = "woo.binding"
    _inherits = {"product.product": "odoo_id"}
    _description = "WooCommerce Product"

    _rec_name = "name"

    RECOMPUTE_QTY_STEP = 1000  # products at a time

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

    def export_inventory(self, fields=None):
        """Export the Quantity of a Product."""
        self.ensure_one()
        with self.backend_id.work_on(self._name) as work:
            exporter = work.component(usage="product.inventory.exporter")
            return exporter.run(self, fields)

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
        backends = defaultdict(set)
        for product in self:
            backends[product.backend_id].add(product.id)
        for backend, product_ids in backends.items():
            self._recompute_woo_qty_backend(backend, self.browse(product_ids))
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

        location = self.env["stock.location"]
        if self.env.context.get("location"):
            location = location.browse(self.env.context["location"])
        else:
            location = backend.warehouse_id.lot_stock_id
        product_fields = ["woo_product_qty", stock_field]
        if read_fields:
            product_fields += read_fields

        self_with_location = self.with_context(location=location.id)
        for chunk_ids in chunks(products.ids, self.RECOMPUTE_QTY_STEP):
            records = self_with_location.browse(chunk_ids)
            for product in records.read(fields=product_fields):
                new_qty = self._woo_qty(product, backend, location, stock_field)
                if new_qty != product["woo_product_qty"]:
                    self.browse(product["id"]).woo_product_qty = new_qty

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
    }


class WooBindingProductListener(Component):
    _name = "woo.binding.product.product.listener"
    _inherit = "base.connector.listener"
    _apply_on = ["woo.product.product"]

    # fields which should not trigger an export of the products
    # but an export of their inventory
    INVENTORY_FIELDS = (
        "stock_management",
        "woo_product_qty",
    )

    @skip_if(lambda self, record, **kwargs: self.no_connector_export(record))
    def on_record_write(self, record, fields=None):
        inventory_fields = list(set(fields).intersection(self.INVENTORY_FIELDS))
        if inventory_fields:
            record.with_delay(priority=20).export_inventory(fields=inventory_fields)
