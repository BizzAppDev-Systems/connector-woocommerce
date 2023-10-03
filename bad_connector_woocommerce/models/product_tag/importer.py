import logging

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from odoo.addons.connector.exception import MappingError

_logger = logging.getLogger(__name__)


class WooProductTagBatchImporter(Component):
    """Batch Importer the WooCommerce Product Tag"""

    _name = "woo.product.tag.batch.importer"
    _inherit = "woo.batch.importer"
    _apply_on = "woo.product.tag"


class WooProductTagImporter(Component):
    _name = "woo.product.tag.importer"
    _inherit = "woo.importer"
    _apply_on = "woo.product.tag"


class WooProductTagImportMapper(Component):
    _name = "woo.product.tag.import.mapper"
    _inherit = "woo.import.mapper"
    _apply_on = ["woo.product.tag"]

    @mapping
    def name(self, record):
        """Mapping for Name"""
        name = record.get("name")
        if not name:
            raise MappingError(_("Tag Name doesn't exist please check !!!"))
        return {"name": name}
