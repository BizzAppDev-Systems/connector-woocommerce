import logging

from odoo.addons.component.core import Component

# from odoo import _


# from odoo.addons.connector.components.mapper import mapping
# from odoo.addons.connector.exception import MappingError

_logger = logging.getLogger(__name__)


class ProductInventoryExporter(Component):
    _name = "woo.product.product.exporter"
    _inherit = "woo.exporter"
    _apply_on = ["woo.product.product"]
    _usage = "product.inventory.exporter"

    def run(self, binding, record=None, *args, **kwargs):
        """Export the product inventory to WooCommerce"""
        external_id = self.binder.to_external(binding)
        data = {"stock_quantity": binding.woo_product_qty}
        if binding.backend_id.update_stock_inventory and binding.stock_management:
            self.backend_adapter.write(external_id, data)
