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

    children = [
        ("states", "woo_state_line_ids", "woo.res.country.state"),
    ]
    direct = [("code", "external_id"), ("country_id", "woo_country_id")]

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
    def update_woo_country_id(self, record):
        """Update the woo_country_id"""
        woo_country_id = record.get("code")
        if not woo_country_id:
            raise MappingError(_("WooCommerce Country ID not found Please check!!!"))
        woo_country = self.env["woo.res.country"].search(
            [("odoo_id.code", "=", woo_country_id)], limit=1
        )
        self.options.update(woo_country_id=woo_country.id, record=record)
        return {"woo_country_id": woo_country.id}


class WooResCountryImporter(Component):
    """Importer the WooCommerce Country"""

    _name = "woo.res.country.importer"
    _inherit = "woo.importer"
    _apply_on = "woo.res.country"


class WooResCountryStateImportMapper(Component):
    _name = "woo.res.country.state.mapper"
    _inherit = "woo.import.mapper"
    _apply_on = "woo.res.country.state"

    direct = [
        ("code", "woo_state_id"),
        ("code", "external_id"),
        ("name", "name"),
    ]

    @only_create
    @mapping
    def odoo_id(self, record):
        """Creating odoo id"""
        state_code = record.get("code")
        binder_country = self.binder_for("woo.res.country")
        woo_binding_country = binder_country.to_internal(record.get("code"))
        if woo_binding_country:
            return {}
        if not state_code:
            raise MappingError(
                _("Country doesn't exist for %s !!!") % record.get("code")
            )
        country_state = self.env["res.country.state"].search(
            [
                ("code", "=", state_code),
                ("country_id", "=", woo_binding_country.odoo_id.id),
            ],
            limit=1,
        )
        if not country_state:
            return {}
        return {"odoo_id": country_state.id}

    def get_country(self, record):
        country_rec = record.get("code")
        if not country_rec:
            return False
        binder = self.binder_for("woo.res.country")
        country = binder.to_internal(country_rec)
        return country

    @mapping
    def country_id(self, record):
        country_rec = record.get("code")
        if not country_rec:
            return {}
        country = self.get_country(record)
        return {"country_id": country.id}

    @mapping
    def code(self, record):
        country_rec = record.get("code")
        if not country_rec:
            raise MappingError(
                _("State Code doesn't exist for %s !!!") % record.get("code")
            )
        return {"code": country_rec}

    @mapping
    def woo_country_id(self, record):
        """Mapping for Woo Country ID"""
        return {"woo_country_id": self.options.get("woo_country_id")}


class WooResCountryStateImporter(Component):
    _name = "woo.res.country.state.importer"
    _inherit = "woo.map.child.import"
    _apply_on = "woo.res.country.state"
