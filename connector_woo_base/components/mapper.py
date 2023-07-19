from odoo.addons.component.core import AbstractComponent


class WooImporttMapper(AbstractComponent):
    """Base Importer Mapper for woocommerce"""

    _name = "woo.import.mapper"
    _inherit = ["connector.woo.base", "base.import.mapper"]
    _usage = "import.mapper"


class WooExportMapper(AbstractComponent):
    """Base Exporter Mapper for woocommerce"""

    _name = "woo.export.mapper"
    _inherit = ["connector.woo.base", "base.export.mapper"]
    _usage = "export.mapper"
