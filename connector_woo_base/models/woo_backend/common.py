import logging
from contextlib import contextmanager

from odoo import fields, models

from ...components.backend_adapter import WooAPI, WooLocation
from datetime import datetime, timedelta

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
    order_prefix = fields.Char(string="Sale Order Prefix", default="WOO_")

    def toggle_test_mode(self):
        """Test Mode"""
        for record in self:
            record.test_mode = not record.test_mode

    @contextmanager
    def work_on(self, model_name, **kwargs):
        """Add the work on for woo."""
        self.ensure_one()
        location = self.location
        client_id = self.client_id
        client_secret = self.client_secret

        if self.test_mode:
            location = self.test_location
            client_id = self.test_client_id
            client_secret = self.test_client_secret

        woo_location = WooLocation(
            location=location,
            client_id=client_id,
            client_secret=client_secret,
            version=self.version,
            test_mode=self.test_mode,
        )

        with WooAPI(woo_location) as woo_api:
            with super(WooBackend, self).work_on(
                model_name, woo_api=woo_api, **kwargs
            ) as work:
                yield work

    def _import_from_date(
        self,
        model,
        from_date_field,
        filters=None,
        force_update_field=None,
        priority=None,
        from_date_field_ext=None,
    ):
        """Common method for import data from from_date."""
        if not filters:
            filters = {}
        import_start_time = datetime.now()
        job_options = {}
        if priority or priority == 0:
            job_options["priority"] = priority
        for backend in self:
            from_date = backend[from_date_field]
            if not from_date:
                from_date = None
            if from_date and from_date_field_ext:
                filters[from_date_field_ext] = from_date
            force = False
            if force_update_field:
                force = backend[force_update_field]
            self.env[model].sudo().with_delay(**job_options or {}).import_batch(
                backend, filters=filters, force=force
            )
            if force:
                backend[force_update_field] = False
        next_time = import_start_time - timedelta(seconds=IMPORT_DELTA_BUFFER)
        self.write({from_date_field: next_time})
