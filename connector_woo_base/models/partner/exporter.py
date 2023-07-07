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

    def get_address_1(self, record):
        """Mapping for address"""
        address = record.street or ""
        return {"address_1": address}

    def get_address_2(self, record):
        """Mapping for address2"""
        address2 = record.street2 or ""
        return {"address_2": address2}

    def get_city(self, record):
        """Mappinf for City"""
        city = record.city or ""
        return {"city": city}

    def get_phone(self, record):
        """Mapping for Phone"""
        phone = record.phone or ""
        return {"phone": phone}

    def get_state(self, record):
        """Mapping for state"""
        state = record.state_id.name or ""
        return {"state": state}

    def get_company(self, record):
        """Mapping for company"""
        company = record.company_id.name or ""
        return {"company": company}

    @mapping
    def billing(self, move):
        """Mapping for billing"""
        fields_lst = [
            "address_1",
            "address_2",
            "city",
            "phone",
            "company",
        ]
        data = {}
        for field in fields_lst:
            data.update(getattr(self, "get_%s" % (field))(move))
        return {"billing": data}


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
        partners = self.env["res.partner"].search(domain)
        for partner in partners:
            self._export_record(partner)
            partner.message_post(body=_("Partner Exported via Woo interface"))
