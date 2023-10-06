import logging

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create
from odoo.addons.connector.exception import MappingError

# pylint: disable=W7950

_logger = logging.getLogger(__name__)


class WooTaxBatchImporter(Component):
    """Batch Importer for WooCommerce Tax"""

    _name = "woo.tax.batch.importer"
    _inherit = "woo.batch.importer"
    _apply_on = "woo.tax"


class WooTaxImportMapper(Component):
    """Impoter Mapper for the WooCommerce Tax"""

    _name = "woo.tax.import.mapper"
    _inherit = "woo.import.mapper"
    _apply_on = "woo.tax"

    @only_create
    @mapping
    def odoo_id(self, record):
        total_rate = record.get("rate")
        tax = self.env["account.tax"].search([("account", "=", total_rate)], limit=1)
        if not tax:
            return {}
        return {"odoo_id": tax.id}

    @mapping
    def name(self, record):
        """Mapping for name of tax"""
        name = record.get("name")
        if not name:
            raise MappingError(_("No Tax Name found in Response"))
        return {"name": name}

    @mapping
    def amount(self, record):
        """Mapping for amount"""
        return {"amount": record.get("rate")} if record.get("rate") else {}


class WooTaxImporter(Component):
    """Importer the WooCommerce Tax"""

    _name = "woo.tax.importer"
    _inherit = "woo.importer"
    _apply_on = "woo.tax"
