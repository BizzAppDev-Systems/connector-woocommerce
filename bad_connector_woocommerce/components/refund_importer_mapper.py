# import json

from odoo.addons.component.core import AbstractComponent

# from odoo.addons.connector.components.mapper import mapping


class WooRefundImporttMapper(AbstractComponent):
    """Base Refund Importer Mapper for woocommerce"""

    _name = "woo.refund.import.mapper"
    _inherit = ["connector.woo.base", "base.import.mapper"]
    # _usage = "refund.import.mapper"
    _base_mapper_usage = "woo.refund.import.mapper"

    # @mapping
    # def backend_id(self, record):
    #     """Return backend."""
    #     return {"backend_id": self.backend_record.id}

    # @mapping
    # def woo_data(self, record):
    #     """Return woo data."""
    #     return {"woo_data": json.dumps(record, indent=2)}
