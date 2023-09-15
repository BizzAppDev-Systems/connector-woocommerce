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
    _description = "WooCommerce Backend"
    _inherit = ["mail.thread", "connector.backend"]

    name = fields.Char(
        string="Name", required=True, help="Enter the name of the WooCommerce backend."
    )
    version = fields.Selection(
        selection=[("v3", "V3")],
        default="v3",
        required=True,
        string="Version",
        help="Select the WooCommerce API version you want to use.",
    )
    default_limit = fields.Integer(
        string="Default Limit",
        default=10,
        help="Set the default limit for data imports.",
    )
    company_id = fields.Many2one(comodel_name="res.company", string="Company")
    location = fields.Char(
        string="Location(Live)", help="Enter the Live Location for WooCommerce."
    )
    client_id = fields.Char(
        string="Client ID(Live)",
        help="Enter the Client ID for Live Mode (Username for Basic Authentication).",
    )
    client_secret = fields.Char(
        string="Secret key(Live)",
        help="Enter the Secret Key for Live Mode (Password for Basic Authentication).",
    )
    test_mode = fields.Boolean(
        string="Test Mode", default=True, help="Toggle between Test and Live modes."
    )
    test_location = fields.Char(
        string="Test Location", help="Enter the Test Location for WooCommerce."
    )
    test_client_id = fields.Char(
        string="Client ID",
        help="Enter the Client ID for Test Mode (Username for Basic Authentication).",
    )
    test_client_secret = fields.Char(
        string="Secret key",
        help="Enter the Secret Key for Test Mode (Password for Basic Authentication).",
    )

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

    def _import_from_date(self, model, from_date_field, priority=None, filters=None):
        """Method to add a filter based on the date."""
        import_start_time = datetime.now()
        job_options = {}
        if priority or priority == 0:
            job_options["priority"] = priority
        from_date = self[from_date_field]
        if from_date:
            filters["after"] = fields.Datetime.to_string(from_date)
            filters['dates_are_gmt'] = True
        self.env[model].with_delay(**job_options or {}).import_batch(
            backend=self, filters=filters
        )
        # Records from Woo are imported based on their `created_at`
        # date.  This date is set on Woo at the beginning of a
        # transaction, so if the import is run between the beginning and
        # the end of a transaction, the import of a record may be
        # missed.  That's why we add a small buffer back in time where
        # the eventually missed records will be retrieved.  This also
        # means that we'll have jobs that import twice the same records,
        # but this is not a big deal because they will be skipped when
        # the last `sync_date` is the same.
        next_time = import_start_time - timedelta(seconds=IMPORT_DELTA_BUFFER)
        next_time = fields.Datetime.to_string(next_time)
        self.write({from_date_field: next_time})
