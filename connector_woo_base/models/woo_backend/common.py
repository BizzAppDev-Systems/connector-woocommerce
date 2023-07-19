import logging
from contextlib import contextmanager

from odoo import fields, models

from ...components.backend_adapter import WooAPI, WooLocation

_logger = logging.getLogger(__name__)


IMPORT_DELTA_BUFFER = 30  # seconds


class WooBackend(models.Model):
    """Backend for WooCommerce"""

    _name = "woo.backend"
    _description = "Woo Backend"
    _inherit = ["mail.thread", "connector.backend"]

    name = fields.Char(string="Name", required=True)
    version = fields.Selection(
        selection=[("v0", "V0"), ("v1", "V1"), ("v3", "V3")],
        default="v3",
        required=True,
        string="Version",
    )
    default_limit = fields.Integer(string="Default Limit", default=10)
    company_id = fields.Many2one(comodel_name="res.company", string="Company")
    export_partner_from_date = fields.Datetime(string="Export partner from date")
    import_partner_from_date = fields.Datetime(string="Import partner from date")
    location = fields.Char(string="Location (Live)")
    test_location = fields.Char(string="Location (Live)")
    client_id = fields.Char(string="Client ID")
    client_secret = fields.Char(string="Secret key")
    test_mode = fields.Boolean(string="Test Mode", default=True)
    test_location = fields.Char(string="Test Location")
    test_client_id = fields.Char(string="Client ID")
    test_client_secret = fields.Char(string="Secret key")
    force_import_partner = fields.Boolean(string="Force Import(Partner)")

    def toggle_test_mode(self):
        """Test Mode"""
        for record in self:
            record.test_mode = not record.test_mode

    @contextmanager
    def work_on(self, model_name, **kwargs):
        """Add the work on for woo."""
        self.ensure_one()
        location = self.test_location
        version = self.version
        client_id = self.test_client_id
        client_secret = self.test_client_secret
        if not self.test_mode:
            location = self.location
            client_id = self.client_id
            client_secret = self.client_secret
        woo_location = WooLocation(
            location=location,
            client_id=client_id,
            client_secret=client_secret,
            version=version,
            test_mode=self.test_mode,
        )
        with WooAPI(woo_location) as woo_api:
            _super = super(WooBackend, self)
            # from the components we'll be able to do: self.work.woo_api
            with _super.work_on(model_name, woo_api=woo_api, **kwargs) as work:
                yield work
