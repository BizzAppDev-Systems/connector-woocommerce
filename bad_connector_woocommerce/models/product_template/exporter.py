import logging

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping

_logger = logging.getLogger(__name__)


class WooProductTemplateExporterMapper(Component):
    _name = "woo.product.template.export.mapper"
    _inherit = "woo.export.mapper"
    _apply_on = "woo.product.template"

    @mapping
    def stock_quantity(self, record):
        """Mapping for stock_quantity"""
        return {"stock_quantity": record.woo_bind_ids[0].woo_product_qty}


class ProductTemplateInventoryExporter(Component):
    _name = "woo.product.template.exporter"
    _inherit = "woo.exporter"
    _apply_on = ["woo.product.template"]
