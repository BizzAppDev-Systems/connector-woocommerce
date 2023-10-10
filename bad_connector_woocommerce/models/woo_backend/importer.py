from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from odoo.addons.connector.exception import MappingError


class WooBackendBatchImporter(Component):
    """Batch Importer the WooCommerce Backend"""

    _name = "woo.backend.batch.importer"
    _inherit = "woo.batch.importer"
    _apply_on = "woo.backend"


class WooBackendImporter(Component):
    _name = "woo.backend.importer"
    _inherit = "woo.importer"
    _apply_on = "woo.backend"


class WooBackendImportMapper(Component):
    _name = "woo.backend.import.mapper"
    _inherit = "woo.import.mapper"
    _apply_on = ["woo.backend"]

    @mapping
    def pricelist_id(self, record):
        """Mapping for Name"""
        name = record.get("name")
        if not name:
            raise MappingError(_("Attribute Value Name doesn't exist please check !!!"))
        return {"pricelist_id": record.get("name")}
