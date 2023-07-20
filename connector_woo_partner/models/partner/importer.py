import logging

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create

# pylint: disable=W7950

_logger = logging.getLogger(__name__)


class WooResPartnerBatchImporter(Component):
    """Batch Importer the WooCommerce Partner"""

    _name = "woo.res.partner.batch.importer"
    _inherit = "woo.delayed.batch.importer"
    _apply_on = "woo.res.partner"


class WooResPartnerImportMapper(Component):
    """Impoter Mapper for the WooCommerce Partner"""

    _name = "woo.res.partner.import.mapper"
    _inherit = "woo.import.mapper"
    _apply_on = "woo.res.partner"

    _sql_constraints = [
        ("woo_res_partner_email_unique", "UNIQUE(email)", "Email must be unique!")
    ]

    @only_create
    @mapping
    def name(self, record):
        """Mapping for name"""
        username = record.get("username")
        return {"name": username}

    @only_create
    @mapping
    def odoo_id(self, record):
        """Will bind the partner to an existing one with the same code"""
        binder = self.binder_for(model="woo.res.partner")
        woo_partner = binder.to_internal(record.get("id"), unwrap=True)
        if woo_partner:
            return {"odoo_id": woo_partner.id}
        return {}

    @mapping
    def email(self, record):
        """Mapping for Email"""
        email = record.get("email")
        return {"email": email}

    @mapping
    def street(self, record):
        """Mapping for street"""
        address = record.get("billing", {}).get("address1") or ""
        return {"street": address}

    @mapping
    def street2(self, record):
        """Mapping for street2"""
        address2 = record.get("billing", {}).get("address2") or ""
        return {"street2": address2}

    @mapping
    def city(self, record):
        """Mapping for city"""
        city = record.get("billing", {}).get("city") or ""
        return {"city": city}

    @mapping
    def company_id(self, record):
        """Mapping for company"""
        company = record.get("billing", {}).get("company") or ""
        return {"company_id": company}

    @mapping
    def backend_id(self, record):
        """Return backend."""
        return {"backend_id": self.backend_record.id}


class WooResPartnerImporter(Component):
    """Importer the WooCommerce Partner"""

    _name = "woo.res.partner.importer"
    _inherit = "woo.importer"
    _apply_on = "woo.res.partner"
