import logging
from contextlib import contextmanager
from datetime import datetime, timedelta

from odoo import api, fields, models

from ...components.backend_adapter import WooAPI, WooLocation

_logger = logging.getLogger(__name__)


IMPORT_DELTA_BUFFER = 30  # seconds


class WooBackend(models.Model):
    """Backend for WooCommerce"""

    _name = "woo.backend"
    _description = "WooCommerce Backend"
    _inherit = ["mail.thread", "connector.backend"]

    name = fields.Char(
        string="Name", required=True, help="Enter the name of the WooCommerce backend."
    )
    version = fields.Selection(
        selection=[("wc/v3", "V3")],
        default="wc/v3",
        required=True,
        help="Select the WooCommerce API version you want to use.",
    )
    default_limit = fields.Integer(
        string="Default Limit",
        default=10,
        help="Set the default limit for data imports.",
    )
    company_id = fields.Many2one(comodel_name="res.company", string="Company")
    location = fields.Char(
        string="Location(Live)", help="Enter the Live Location for WooCommerce."
    )
    client_id = fields.Char(
        string="Client ID(Live)",
        help="Enter the Client ID for Live Mode (Username for Basic Authentication).",
    )
    client_secret = fields.Char(
        string="Secret key(Live)",
        help="Enter the Secret Key for Live Mode (Password for Basic Authentication).",
    )
    test_mode = fields.Boolean(
        string="Test Mode", default=True, help="Toggle between Test and Live modes."
    )
    test_location = fields.Char(
        string="Test Location", help="Enter the Test Location for WooCommerce."
    )
    test_client_id = fields.Char(
        string="Client ID",
        help="Enter the Client ID for Test Mode (Username for Basic Authentication).",
    )
    test_client_secret = fields.Char(
        string="Secret key",
        help="Enter the Secret Key for Test Mode (Password for Basic Authentication).",
    )
    mark_completed = fields.Boolean(
        string="Mark Order Completed On Delivery",
        help="""If Mark Completed is True,
        we can update the sale order status export functionality
        for WooCommerce orders whose status is not completed.""",
    )
    tracking_info = fields.Boolean(
        string="Send Tracking Information",
        help="""If Mark Completed is True, this field will be visible,
        and we can add tracking information at the DO (Delivery Order) level to
        update the sale order status as well as Tracking Info in WooCommerce.""",
    )
    import_orders_from_date = fields.Datetime(string="Import Orders from date")
    order_prefix = fields.Char(string="Sale Order Prefix", default="WOO_")
    import_products_from_date = fields.Datetime(string="Import products from date")
    without_sku = fields.Boolean(
        string="Allow Product without SKU",
        help="""If this Boolean is set to True, the system will import products
        that do not have an assigned SKU. Please enable this option if you want
        to include products without SKU in the import process.""",
    )
    product_categ_id = fields.Many2one(
        comodel_name="product.category",
        string="Product Category",
        required=True,
        help="Set Odoo Product Category for imported WooCommerce products.",
    )
    import_partners_from_date = fields.Datetime(string="Import partners from date")
    without_email = fields.Boolean(
        string="Allow Partners without Email",
        help="""When the boolean is 'True,' partners can be imported without needing
        an email address.""",
    )

    def _import_from_date(self, model, from_date_field, priority=None, filters=None):
        """Method to add a filter based on the date."""
        import_start_time = datetime.now()
        job_options = {}
        if priority or priority == 0:
            job_options["priority"] = priority
        from_date = self[from_date_field]
        if from_date:
            filters["modified_after"] = fields.Datetime.to_string(from_date)
            filters["dates_are_gmt"] = True
        self.env[model].with_delay(**job_options or {}).import_batch(
            backend=self, filters=filters
        )
        # Records from Woo are imported based on their `created_at`
        # date.  This date is set on Woo at the beginning of a
        # transaction, so if the import is run between the beginning and
        # the end of a transaction, the import of a record may be
        # missed.  That's why we add a small buffer back in time where
        # the eventually missed records will be retrieved.  This also
        # means that we'll have jobs that import twice the same records,
        # but this is not a big deal because they will be skipped when
        # the last `sync_date` is the same.
        next_time = import_start_time - timedelta(seconds=IMPORT_DELTA_BUFFER)
        next_time = fields.Datetime.to_string(next_time)
        self.write({from_date_field: next_time})

    def toggle_test_mode(self):
        """Test Mode"""
        for record in self:
            record.test_mode = not record.test_mode

    @contextmanager
    def work_on(self, model_name, **kwargs):
        """Add the work on for woo."""
        self.ensure_one()
        location = self.location
        client_id = self.client_id
        client_secret = self.client_secret

        if self.test_mode:
            location = self.test_location
            client_id = self.test_client_id
            client_secret = self.test_client_secret

        woo_location = WooLocation(
            location=location,
            client_id=client_id,
            client_secret=client_secret,
            version=self.version,
            test_mode=self.test_mode,
        )

        with WooAPI(woo_location) as woo_api:
            with super(WooBackend, self).work_on(
                model_name, woo_api=woo_api, **kwargs
            ) as work:
                yield work

    def import_partners(self):
        """Import Partners from backend"""
        filters = {"page": 1}
        for backend in self:
            filters.update({"per_page": backend.default_limit})
            backend.env["woo.res.partner"].with_delay(priority=5).import_batch(
                backend=backend, filters=filters
            )

    @api.model
    def cron_import_partners(self, domain=None):
        backend_ids = self.search(domain or [])
        backend_ids.import_partners()

    def import_products(self):
        """Import Products from backend"""
        filters = {"page": 1}
        for backend in self:
            filters.update({"per_page": backend.default_limit})
            backend._import_from_date(
                model="woo.product.product",
                from_date_field="import_products_from_date",
                priority=5,
                filters=filters,
            )
        return True

    @api.model
    def cron_import_products(self, domain=None):
        """Cron for import_products"""
        backend_ids = self.search(domain or [])
        backend_ids.import_products()

    def import_product_attributes(self):
        """Import Product Attribute from backend"""
        filters = {"page": 1}
        for backend in self:
            filters.update({"per_page": backend.default_limit})
            backend.env["woo.product.attribute"].with_delay(priority=5).import_batch(
                backend=backend, filters=filters
            )

    @api.model
    def cron_import_product_attributes(self, domain=None):
        """Cron for import_product_attributes"""
        backend_ids = self.search(domain or [])
        backend_ids.import_product_attributes()

    def import_product_categories(self):
        """Import Product Category from backend"""
        filters = {"page": 1}
        for backend in self:
            filters.update({"per_page": backend.default_limit})
            backend.env["woo.product.category"].with_delay(priority=5).import_batch(
                backend=backend, filters=filters
            )

    @api.model
    def cron_import_product_categories(self, domain=None):
        """Cron for import_product_categories"""
        backend_ids = self.search(domain or [])
        backend_ids.import_product_categories()

    def import_sale_orders(self):
        """Import Orders from backend"""
        filters = {"page": 1}
        for backend in self:
            filters.update({"per_page": backend.default_limit})
            backend._import_from_date(
                model="woo.sale.order",
                from_date_field="import_orders_from_date",
                priority=5,
                filters=filters,
            )
        return True

    @api.model
    def cron_import_sale_orders(self, domain=None):
        """Cron for import_sale_orders"""
        backend_ids = self.search(domain or [])
        backend_ids.import_sale_orders()

    def export_sale_order_status(self):
        """Export Sale Order Status"""
        for backend in self:
            sale_orders = self.env["sale.order"].search(
                [
                    ("woo_bind_ids.backend_id", "=", backend.id),
                    ("woo_order_status", "!=", "completed"),
                    ("picking_ids.state", "=", "done"),
                ]
            )
            for sale_order in sale_orders:
                sale_order.with_context(execute_from_cron=True).export_delivery_status()

    @api.model
    def cron_export_sale_order_status(self, domain=None):
        """Cron of Export sale order status"""
        backend_ids = self.search(domain or [])
        backend_ids.export_sale_order_status()
