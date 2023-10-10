import logging

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from odoo.addons.connector.exception import MappingError

# pylint: disable=W7950

_logger = logging.getLogger(__name__)


class WooSettingsBatchImporter(Component):
    """Batch Importer the WooCommerce Settings"""

    _name = "woo.settings.batch.importer"
    _inherit = "woo.batch.importer"
    _apply_on = "woo.settings"


class WooSettingsImportMapper(Component):
    """Impoter Mapper for the WooCommerce Settings"""

    _name = "woo.settings.import.mapper"
    _inherit = "woo.import.mapper"
    _apply_on = "woo.settings"

    @mapping
    def name(self, record):
        """Mapping for Name"""
        name = record.get("label")
        if not name:
            raise MappingError(_("Settings Name doesn't exist please check !!!"))
        return {"name": name}

    @mapping
    def woo_type(self, record):
        """Mapping for Type"""
        return {"woo_type": record.get("type")} if record.get("type") else {}

    @mapping
    def default(self, record):
        """Mapping for default"""
        return {"default": record.get("default")} if record.get("default") else {}

    # @mapping
    # def tip(self, record):
    #     """Mapping for tip"""
    #     return {"tip": record.get("tip")} if record.get("tip") else {}

    @mapping
    def value(self, record):
        """Mapping for value"""
        return {"value": record.get("value")} if record.get("value") else {}

    # @mapping
    # def options(self, record):
    #     """Mapping for options"""
    #     return {"options": record.get("options")} if record.get("options") else {}

    # @mapping
    # def description(self, record):
    #     """Mapping for description"""
    #     return {"name": record.get("description")} if record.get("description") else {}


class WooSettingsImporter(Component):
    """Importer the WooCommerce Settings"""

    _name = "woo.settings.importer"
    _inherit = "woo.importer"
    _apply_on = "woo.settings"

    def _after_import(self, binding, **kwargs):
        """Inherit Method: inherit method to import remote child"""
        result = super(WooSettingsImporter, self)._after_import(binding, **kwargs)
        include_tax = False
        if (
            binding.external_id == "woocommerce_prices_include_tax"
            and binding.value == "yes"
        ):
            include_tax = True
            binding.backend_id.write({"include_tax": include_tax})
        return result
