from odoo import models


class WooBackend(models.Model):
    """Backend for WooCommerce"""

    _inherit = "woo.backend"

    def import_products(self):
        """Override the method to also import grouped type products"""
        for backend in self:
            backend._sync_from_date(
                model="woo.product.product",
                from_date_field="import_products_from_date",
                priority=5,
                export=False,
                force_update_field="force_import_products",
            )
        return True
