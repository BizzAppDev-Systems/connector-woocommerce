import logging

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping

_logger = logging.getLogger(__name__)


class WooProductProductExporterMapper(Component):
    _name = "woo.product.product.export.mapper"
    _inherit = "woo.export.mapper"
    _apply_on = "woo.product.product"

    @mapping
    def stock_quantity(self, record):
        """Mapping for stock_quantity"""
        return {"stock_quantity": record.woo_bind_ids.woo_product_qty}


class ProductInventoryExporter(Component):
    _name = "woo.product.product.exporter"
    _inherit = "woo.exporter"
    _apply_on = ["woo.product.product"]
