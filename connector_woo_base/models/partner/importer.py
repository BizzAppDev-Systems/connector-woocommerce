import logging
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create

# pylint: disable=W7950

_logger = logging.getLogger(__name__)


class PartnerBatchImporter(Component):
    _name = "woo.partner.batch.importer"
    _inherit = "woo.delayed.batch.importer"
    _apply_on = "woo.res.partner"

    def run(self, filters=None, force=False, job_options=None):
        """Override Method : Run the synchronization."""
        result = self.backend_adapter.search_read(filters=filters)
        for record in result:
            partners = record.get("id")
            self._import_record(
                external_id=partners,
                job_options=job_options,
                data=record,
            )

    def _import_record(self, external_id, job_options=None, **kwargs):
        """Delay the import of the records"""
        job_options = job_options or {}
        if "priority" not in job_options:
            job_options["priority"] = 20
        return super(PartnerBatchImporter, self)._import_record(
            external_id, job_options, **kwargs
        )


class PartnerImportMapper(Component):
    _name = "woo.partner.import.mapper"
    _inherit = "woo.import.mapper"
    _apply_on = "woo.res.partner"

    direct = [
        ("id", "woo_id"),
        ("email", "email"),
    ]

    @only_create
    @mapping
    def name(self, record):
        """Return Partner"""
        username = record.get("username")
        return {"name": username}

    @mapping
    def email(self, record):
        """Return Email."""
        email = record.get("email")
        return {"email": email}

    @mapping
    def street(self, record):
        address = record.get("billing", {}).get("address1") or ""
        return {"street": address}

    @mapping
    def street2(self, record):
        address2 = record.get("billing", {}).get("address2") or ""
        return {"street2": address2}

    @mapping
    def city(self, record):
        city = record.get("billing", {}).get("city") or ""
        return {"city": city}

    @mapping
    def phone(self, record):
        phone = record.get("billing", {}).get("phone") or ""
        return {"phone": phone}

    @mapping
    def state_id(self, record):
        state = record.get("billing", {}).get("state") or ""
        return {"state_id": state}

    @mapping
    def company_id(self, record):
        company = record.get("billing", {}).get("company") or ""
        return {"company_id": company}

    @mapping
    def external_id(self, record):
        """Return External ID"""
        return {"external_id": record["id"]}

    @mapping
    def backend_id(self, record):
        """Return backend."""
        return {"backend_id": self.backend_record.id}


class PartnerImporter(Component):
    _name = "woo.partner.importer"
    _inherit = "woo.importer"
    _apply_on = "woo.res.partner"

    def _after_import(self, partner_binding):
        """Import the partners ?"""
        pass
