import logging

from odoo.addons.component.core import Component

# from odoo import _


# from odoo.addons.connector.components.mapper import mapping
# from odoo.addons.connector.exception import MappingError

# pylint: disable=W7950

_logger = logging.getLogger(__name__)


class WooAccountTaxBatchImporter(Component):
    """Batch Importer the WooCommerce Account Tax"""

    _name = "woo.account.tax.batch.importer"
    _inherit = "woo.batch.importer"
    _apply_on = "woo.account.tax"


class WooAccountTaxImportMapper(Component):
    """Impoter Mapper for the WooCommerce Account Tax"""

    _name = "woo.account.tax.import.mapper"
    _inherit = "woo.import.mapper"
    _apply_on = "woo.account.tax"


class WooAccountTaxImporter(Component):
    """Importer the WooCommerce Tax"""

    _name = "woo.account.tax.importer"
    _inherit = "woo.importer"
    _apply_on = "woo.account.tax"
