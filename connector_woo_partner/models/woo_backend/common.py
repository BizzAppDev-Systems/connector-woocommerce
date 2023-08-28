from odoo import models, fields
from datetime import datetime, timedelta

IMPORT_DELTA_BUFFER = 30


class WooBackend(models.Model):
    """Backend for WooCommerce"""

    _inherit = "woo.backend"
    import_partners_from_date = fields.Datetime(string="Import partners from date")

    def _import_from_date(self, model, from_date_field, priority=None, filters=None):
        """Method to add a filter based on the date."""
        import_start_time = datetime.now()
        print(
            import_start_time,
            "aiswishwiswhioshwioshwiodhwidhuiwdhwd",
            "\n\n\n\n\n\n\n\n",
        )
        job_options = {}
        if priority or priority == 0:
            job_options["priority"] = priority
        from_date = self[from_date_field]
        if from_date:
            filters["after"] = self.import_partners_from_date
            print(
                filters, "\n\n\n\nn\n\n\n\n\n\n\n\n\n\n\n\n", "hellllllloooooooooooooo"
            )
            from_date = fields.Datetime.from_string(from_date)
        else:
            from_date = None
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

    def import_partners(self):
        """Import Partners from backend"""
        # filters = {"page": 1}
        # for backend in self:
        #     filters.update({"per_page": backend.default_limit})
        #     backend.env["woo.res.partner"].with_company(backend.company_id).with_delay(
        #         priority=5
        #     ).import_batch(backend=backend, filters=filters)
        filters = {"page": 1}
        for backend in self:
            print(filters.get("date_modified_gmt"),"\n\n\n\n\n\n\n\n\\n\n\n\n\\n\n\n\n\n")
            print(
                self.import_partners_from_date,
                "heloaaaaaaaaaaaaaaaaaaaaaaaaa" "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n",
            )
            filters.update({"per_page": backend.default_limit})
            backend._import_from_date(
                model="woo.res.partner",
                from_date_field="import_partners_from_date",
                priority=5,
                filters=filters,
            )
            print(
                "dujheeeeeeeeeeeeeeeeeeeeeeeeeeee ya ya ya aya ya ay \n\n\n\n\\n\n\n\n\n\n\n"
            )
        return True

    def cron_import_partners(self, domain=None):
        backend_ids = self.search(domain or [])
        backend_ids.import_partners()
