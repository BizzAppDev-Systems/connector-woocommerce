import logging

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from odoo.addons.connector.exception import MappingError

_logger = logging.getLogger(__name__)


class WooResPartnerExporterMapper(Component):
    """Exporter Mapper for the WooCommerce Partner"""

    _name = "woo.res.partner.export.mapper"
    _inherit = "woo.export.mapper"
    _apply_on = "woo.res.partner"

    @mapping
    def email(self, record):
        """Mapping for email"""
        if not record.email:
            # raise mapping error in case of email is missing in product
            raise MappingError(
                _("Failed Export! email missing on partner %s") % (record.name)
            )
        return {"email": record.email}

    @mapping
    def username(self, record):
        """Mapping for Username"""
        username = record.name or ""
        return {"username": username}


class WooResPartnerExporter(Component):
    """Exporter for Woocommerce Partner"""

    _name = "woo.res.partner.exporter"
    _inherit = "woo.exporter"
    _apply_on = "woo.res.partner"


class WooResPartnerBatchExporter(Component):
    """Batch Exporter for Woocommerce Partner"""

    _name = "woo.res.partner.batch.exporter"
    _inherit = "woo.batch.exporter"
    _apply_on = "woo.res.partner"

    def run(self, filters=None):
        """Override Method : Run the synchronization."""
        filters = filters or {}
        domain = filters.get("domain", [])
        if not domain:
            _logger.info(_("Moves: No record found to export(no domain found.)!!!"))
            return
        moves = self.env["res.partner"].search(domain)
        for move in moves:
            self._export_record(move)
            move.message_post(body=_("Partner Exported via Woo interface"))
