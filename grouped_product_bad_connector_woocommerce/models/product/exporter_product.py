import logging

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from odoo.addons.connector.exception import MappingError

_logger = logging.getLogger(__name__)


class WooProductExporterMapper(Component):
    _inherit = "woo.product.export.mapper"

    @mapping
    def type(self, record):
        """Mapping for type"""
        if not record.bom_ids:
            if record.product_template_variant_value_ids:
                return {}
            return {"type": "simple"}
        return {"type": "grouped"}

    @mapping
    def grouped_products(self, record):
        """Mapping for grouped_products"""
        if not record.bom_ids:
            return {}
        product = record.odoo_id
        bom = self.env["mrp.bom"]._bom_find(products=product, bom_type="phantom")
        if not bom[product]:
            return {}
        grouped_products = []
        for bom_product in bom[product].bom_line_ids:
            if not bom_product.product_id.woo_bind_ids:
                raise MappingError(
                    _(
                        """Product doesn't found in WooCommerce.
                        Please export the Product '%s' to WooCommerce"""
                        % bom_product.product_id.name
                    )
                )
            grouped_products.append(bom_product.product_id.woo_bind_ids[0].external_id)
        return {"grouped_products": grouped_products}
