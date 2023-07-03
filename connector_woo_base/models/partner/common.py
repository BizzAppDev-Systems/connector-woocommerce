import logging

from odoo import api, fields, models

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    woo_bind_ids = fields.One2many(
        comodel_name="woo.res.partner",
        inverse_name="odoo_id",
        string="Woo Bindings",
        copy=False,
    )

    woo_address_bind_ids = fields.One2many(
        comodel_name="woo.address",
        inverse_name="odoo_id",
        string="Woo Address Bindings",
        copy=False,
    )
    woo_id = fields.Char()

    def export_partner(self):
        """Export Product to the Woo"""
        pass

    @api.model
    def import_batch(self, backend, filters=None):
        """Import batch for res.partner"""
        return super(ResPartner, self).import_batch(backend, filters=filters)


class WooResPartner(models.Model):
    _name = "woo.res.partner"
    _inherit = "woo.binding"
    _inherits = {"res.partner": "odoo_id"}
    _description = "Woo Partner"

    _rec_name = "name"

    odoo_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        required=True,
        ondelete="restrict",
    )

class ResPartnerAdapter(Component):
    _name = "woo.res.partner.adapter"
    _inherit = "woo.adapter"
    _apply_on = "woo.res.partner"

    _woo_model = "wc/{version}/customers"
    _woo_search = "Customer"
    _woo_key = "id"
    _odoo_ext_id_key = "woo_id"


class WooAddress(models.Model):
    _name = "woo.address"
    _inherit = "woo.binding"
    _inherits = {"res.partner": "odoo_id"}
    _description = "Woo Address"

    _rec_name = "backend_id"

    odoo_id = fields.Many2one(
        comodel_name="res.partner", string="Partner", required=True, ondelete="restrict"
    )
    created_at = fields.Datetime(string="Created At (on woo)", readonly=True)
    updated_at = fields.Datetime(string="Updated At (on woo)", readonly=True)

    woo_partner_id = fields.Many2one(
        comodel_name="woo.res.partner",
        string="Woo Partner",
        required=True,
        ondelete="cascade",
    )
    backend_id = fields.Many2one(
        related="woo_partner_id.backend_id",
        comodel_name="woo.backend",
        string="Woo Backend",
        store=True,
        readonly=True,
        # override 'woo.binding', can't be INSERTed if True:
        required=False,
    )
