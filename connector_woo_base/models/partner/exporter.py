import logging
from odoo import _
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from odoo.addons.connector.exception import MappingError

_logger = logging.getLogger(__name__)


class PartnerExporterMapper(Component):
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

    # def get_street(self, record):
    #     address = record.street or ""
    #     return {"street": address}

    # def get_street2(self, record):
    #     address2 = record.street2 or ""
    #     return {"street2": address2}

    # def get_city(self, record):
    #     city = record.city or ""
    #     return {"city": city}

    # def get_phone(self, record):
    #     phone = record.phone or ""
    #     return {"phone": phone}

    # def get_state(self, record):
    #     state = record.state_id.name or ""
    #     return {"state": state}

    # def get_company(self, record):
    #     company = record.company_id.name or ""
    #     return {"company": company}

    # @mapping
    # def billing(self, move):
    #     """Create list for the items mapping field"""
    #     fields_lst = [
    #         "street",
    #         "street2",
    #         "city",
    #         "phone",
    #         "company",
    #     ]
    #     data = {}
    #     for field in fields_lst:
    #         data.update(getattr(self, "get_%s" % (field))(move))
    #     return data


class PartnerExporter(Component):
    _name = "woo.account.move.exporter"
    _inherit = "woo.exporter"
    _apply_on = "woo.res.partner"


class PartnerBatchExporter(Component):
    _name = "woo.res.partner.exporter"
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

    def _export_record(self, record, job_options=None, **kwargs):
        """Inherit Method: Delay the export of the records."""
        job_options = job_options or {}
        if "priority" not in job_options:
            job_options["priority"] = 20
        return super(PartnerBatchExporter, self)._export_record(record)
