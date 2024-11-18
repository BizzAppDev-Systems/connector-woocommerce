import logging

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping

_logger = logging.getLogger(__name__)


class WooProductProductExporterMapper(Component):
    _name = "woo.product.product.export.mapper"
    _inherit = "woo.export.mapper"
    _apply_on = "woo.product.product"
    _usage = "product.exporter.mapper"

    @mapping
    def name(self, record):
        """Mapping for name"""
        return {"name": record.name}

    @mapping
    def sku(self, record):
        """Mapping for default_code"""
        return {"sku": str(record.default_code)}


class WooProductProductExporter(Component):
    _name = "woo.product.product.exporter"
    _inherit = "woo.exporter"
    _apply_on = ["woo.product.product"]
    _usage = "product.exporter"
    _base_mapper_usage = "product.exporter.mapper"
