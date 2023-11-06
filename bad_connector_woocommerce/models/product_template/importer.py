import logging

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from odoo.addons.connector.exception import MappingError

# pylint: disable=W7950

_logger = logging.getLogger(__name__)


class WooProductTemplateBatchImporter(Component):
    """Batch Importer the WooCommerce Product Template"""

    _name = "woo.product.template.batch.importer"
    _inherit = "woo.delayed.batch.importer"
    _apply_on = "woo.product.template"


class WooProductTemplateImportMapper(Component):
    """Impoter Mapper for the WooCommerce Product Template"""

    _name = "woo.product.template.import.mapper"
    _inherit = "woo.import.mapper"
    _apply_on = "woo.product.template"

    @mapping
    def name(self, record):
        """Mapping for Name"""
        name = record.get("name")
        product_tmp_id = record.get("id")
        if not name:
            raise MappingError(
                _("Product Template name doesn't exist for Product ID %s Please check")
                % product_tmp_id
            )
        return {"name": name}


class WooProductTemplateImporter(Component):
    """Importer the WooCommerce Product Template"""

    _name = "woo.product.template.importer"
    _inherit = "woo.importer"
    _apply_on = "woo.product.template"
