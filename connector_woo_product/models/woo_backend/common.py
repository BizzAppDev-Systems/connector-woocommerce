from odoo import models, fields, api

IMPORT_DELTA_BUFFER = 30  # seconds


class WooBackend(models.Model):
    """Backend for WooCommerce"""

    _inherit = "woo.backend"

    import_products_from_date = fields.Datetime(string="Import products from date")
    without_sku = fields.Boolean(
        string="Allow Product without SKU",
        help="If this Boolean is True then it will import those products that do not have assigned SKU.",
    )
    product_categ_id = fields.Many2one(
        comodel_name="product.category",
        string="Product Category",
        required=True,
        help="Set Odoo Product Category for imported WooCommerce products.",
    )

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
