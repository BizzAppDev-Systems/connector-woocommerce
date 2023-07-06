import logging
from contextlib import contextmanager
from datetime import datetime, timedelta

from odoo import fields, models
from odoo.osv import expression

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
    default_limit = fields.Integer(string="Default Limit", default=50)
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

    def _import_from_date(
        self,
        model,
        from_date_field,
        filters=None,
        force_update_field=None,
        priority=None,
    ):
        """This method will give batch data which was import on that date"""
        if not filters:
            filters = {}
        import_start_time = datetime.now()
        job_options = {}
        if priority or priority == 0:
            job_options["priority"] = priority
        for backend in self:
            from_date = backend[from_date_field]
            domain = filters.get("domain", [])
            if from_date:
                domain = expression.AND([domain, [("write_date", ">=", from_date)]])
            domain = expression.AND([domain, [("write_date", "<", import_start_time)]])
            filters["domain"] = domain
            force = False
            if force_update_field:
                force = backend[force_update_field]
            self.env[model].with_company(backend.company_id).with_delay(
                **job_options or {}
            ).import_batch(backend, filters=filters, force=force)
            if force:
                backend[force_update_field] = False
        next_time = import_start_time - timedelta(seconds=IMPORT_DELTA_BUFFER)
        self.write({from_date_field: next_time})

    def _export_from_date(
        self, model, from_date_field, filters=None, priority=None, search_binding=False
    ):
        """Method to add a filter based on the date."""
        if not filters:
            filters = {}
        export_start_time = datetime.now()
        job_options = {}
        if priority or priority == 0:
            job_options["priority"] = priority
        for backend in self:
            from_date = backend[from_date_field]
            if not from_date:
                from_date = None
            domain = filters.get("domain", [])
            date_field = "write_date"
            if from_date:
                domain = expression.AND([domain, [(date_field, ">=", from_date)]])
            domain = expression.AND([domain, [(date_field, "<", export_start_time)]])
            filters["domain"] = domain
            self.env[model].with_company(backend.company_id).with_delay(
                **job_options or {}
            ).export_batch(backend, filters=filters)
        next_time = export_start_time - timedelta(seconds=IMPORT_DELTA_BUFFER)
        self.write({from_date_field: next_time})

    def import_partners(self):
        """Import Partners from backend"""
        for backend in self:
            backend._import_from_date(
                model="woo.res.partner",
                from_date_field="import_partner_from_date",
                priority=5,
                filters={"limit": backend.default_limit, "offset": 0},
            )

    def export_partners(self, filters=None):
        """Export Partners from backend"""
        filters = filters or {}
        for backend in self:
            filters.update(
                {
                    "domain": [
                        "|",
                        ("woo_bind_ids", "=", False),
                        ("woo_bind_ids.external_id", "=", False),
                    ]
                }
            )
            backend._export_from_date(
                model="woo.res.partner",
                from_date_field="export_partner_from_date",
                search_binding=True,
                priority=20,
                filters=filters,
            )
