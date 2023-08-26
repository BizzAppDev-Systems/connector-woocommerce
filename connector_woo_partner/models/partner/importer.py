import logging
from odoo import _
from odoo.addons.component.core import Component
from odoo.addons.connector.exception import MappingError
from odoo.addons.connector.components.mapper import mapping

# pylint: disable=W7950

_logger = logging.getLogger(__name__)


class WooResPartnerBatchImporter(Component):
    """Batch Importer for WooCommerce Partners"""

    _name = "woo.res.partner.batch.importer"
    _inherit = "woo.delayed.batch.importer"
    _apply_on = "woo.res.partner"


class WooResPartnerImportMapper(Component):
    """Impoter Mapper for the WooCommerce Partner"""

    _name = "woo.res.partner.import.mapper"
    _inherit = "woo.import.mapper"
    _apply_on = "woo.res.partner"

    @mapping
    def name(self, record):
        """Mapping for Name (combination of firstname and lastname)"""
        first_name = record.get("first_name", "")
        last_name = record.get("last_name", "")
        full_name = (
            f"{first_name} {last_name}"
            if first_name and last_name
            else first_name or record.get("username", "")
        )
        return {"name": full_name}

    @mapping
    def firstname(self, record):
        """Mapping for firstname"""
        return (
            {"firstname": record.get("first_name")} if record.get("first_name") else {}
        )

    @mapping
    def lastname(self, record):
        """Mapping for lastname"""
        return {"lastname": record.get("last_name")} if record.get("last_name") else {}

    @mapping
    def email(self, record):
        """Mapping for Email"""
        email = record.get("email")
        if not email:
            raise MappingError(_("No Email found in Response"))
        return {"email": email}

    @mapping
    def child_ids(self, record):
        """Mapping for Invoice and Shipping Addresses"""
        woo_res_partner = self.env["res.partner"]
        child_data = woo_res_partner.child(record)
        return {"child_ids": child_data} if child_data else {}

    @mapping
    def backend_id(self, record):
        """Return backend."""
        return {"backend_id": self.backend_record.id}


class WooResPartnerImporter(Component):
    """Importer the WooCommerce Partner"""

    _name = "woo.res.partner.importer"
    _inherit = "woo.importer"
    _apply_on = "woo.res.partner"
