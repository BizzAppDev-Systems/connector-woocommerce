from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
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
        """Mapping for State"""
        state_ids = []
        states = record.get("states", [])
        for state in states:
            state = self.env["res.country.state"].search(
                [
                    ("code", "=", state.get("code")),
                    ("country_id.code", "=", record.get("code")),
                ]
            )
            if not state:
                state_base_on_name = self.env["res.country.state"].search(
                    [
                        ("name", "=", state.get("name")),
                        ("country_id.code", "=", record.get("code")),
                    ]
                )
                if not state_base_on_name:
                    country_state = self.env["res.country.state"].create(
                        {
                            "name": state.get("name"),
                            "code": state.get("code"),
                            # "country_id":,
                        }
                    )
                    state_ids.append(country_state.id)
                state_ids.append(state_base_on_name.id)
            state_ids.append(state.id)
        return {"state_ids": [(6, 0, state_ids)]} if state_ids else {}


class WooResCountryImporter(Component):
    """Importer the WooCommerce Country"""

    _name = "woo.res.country.importer"
    _inherit = "woo.importer"
    _apply_on = "woo.res.country"
