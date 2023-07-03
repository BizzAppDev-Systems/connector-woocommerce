from odoo.addons.component.core import AbstractComponent


class WooImporttMapper(AbstractComponent):
    _name = "woo.import.mapper"
    _inherit = ["connector.woo.base", "base.import.mapper"]
    _usage = "import.mapper"


class WooExportMapper(AbstractComponent):
    _name = "woo.export.mapper"
    _inherit = ["connector.woo.base", "base.export.mapper"]
    _usage = "export.mapper"
