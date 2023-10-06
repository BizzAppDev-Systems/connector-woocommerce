from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create
from odoo.addons.connector.exception import MappingError

# pylint: disable=W7950


class WooResCountryBatchImporter(Component):
    """Batch Importer for WooCommerce Country"""

    _name = "woo.res.country.batch.importer"
    _inherit = "woo.batch.importer"
    _apply_on = "woo.res.country"


class WooResCountryImportMapper(Component):
    """Impoter Mapper for the WooCommerce Country"""

    _name = "woo.res.country.import.mapper"
    _inherit = "woo.import.mapper"
    _apply_on = "woo.res.country"

    direct = [("code", "external_id")]

    @only_create
    @mapping
    def odoo_id(self, record):
        """Creating odoo id"""
        country_code = record.get("code")
        if not country_code:
            raise MappingError(
                _("Country doesn't exist for %s !!!") % record.get("code")
            )
        country = self.env["res.country"].search([("code", "=", country_code)], limit=1)
        if not country:
            return {}
        return {"odoo_id": country.id}

    @mapping
    def name(self, record):
        """Mapping for Name"""
        country_name = record.get("name")
        if not country_name:
            raise MappingError(_("Country Name not found!"))
        return {"name": country_name}

    @mapping
    def code(self, record):
        """Mapping for Code"""
        country_code = record.get("code")
        return {"code": country_code} if country_code else {}

    @mapping
    def state_ids(self, record):
        """Mapper for state_ids"""
        state_ids = []
        states = record.get("states", [])
        if not states:
            return {}
        country_record = self.env["res.country"].search(
            [
                ("code", "=", record.get("code")),
            ],
            limit=1,
        )
        for state in states:
            state_record = self.env["res.country.state"].search(
                [
                    ("code", "=", state.get("code")),
                    ("country_id.code", "=", record.get("code")),
                ],
                limit=1,
            )
            if not state_record:
                state_record = self.env["res.country.state"].search(
                    [
                        ("name", "=", state.get("name")),
                        ("country_id.code", "=", record.get("code")),
                    ],
                    limit=1,
                )
                if not state_record:
                    record_state = {
                        "name": state.get("code"),
                        "code": state.get("code"),
                        "country_id": country_record.id,
                    }
                    state_record = self.env["res.country.state"].create(record_state)
            state_ids.append((4, state_record.id, 0))
        return {"state_ids": state_ids} if state_ids else {}


class WooResCountryImporter(Component):
    """Importer the WooCommerce Country"""

    _name = "woo.res.country.importer"
    _inherit = "woo.importer"
    _apply_on = "woo.res.country"
