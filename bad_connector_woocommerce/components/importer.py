import logging

from odoo.addons.component.core import AbstractComponent

_logger = logging.getLogger(__name__)


class WooImporter(AbstractComponent):
    """Base importer for woocommerce"""

    _name = "woo.importer"
    _inherit = ["base.generic.importer", "connector.woo.base"]
    _usage = "record.importer"

    def _before_import(self, **kwargs):
        if "data" in self.remote_record:
            self.remote_record = self.remote_record.get("data")
        return self.remote_record


class WooMapChildImport(AbstractComponent):
    _name = "woo.map.child.import"
    _inherit = ["connector.woo.base", "generic.map.child.import"]
    _usage = "import.map.child"


class WooBatchImporter(AbstractComponent):
    """
    The role of a BatchImporter is to search for a list of
    items to import, then it can either import them directly or delay
    the import of each item separately.
    """

    _name = "woo.batch.importer"
    _inherit = ["generic.batch.importer", "connector.woo.base"]
    _usage = "batch.importer"

    def run(self, filters=None, force=False, job_options=None, data=None, **kwargs):
        """Run the synchronization"""
        filters = filters or {}
        if "record_count" not in filters:
            filters.update({"record_count": 0})
        data = self.backend_adapter.search(filters)
        records = data.get("data", [])
        for record in records:
            external_id = record.get(self.backend_adapter._remote_ext_id_key)
            self._import_record(external_id, data=record, job_options=job_options)
        filters["record_count"] += len(records)
        record_count = data.get("record_count", 0)
        filters_record_count = filters.get("record_count", 0)
        if (
            record_count is not None
            and filters_record_count is not None
            and int(record_count) > int(filters_record_count)
        ):
            filters.update({"page": filters.get("page", 1) + 1})
            self.process_next_page(
                filters=filters, force=force, job_options=job_options, **kwargs
            )

    def process_next_page(self, filters=None, force=False, job_options=None, **kwargs):
        """Method to trigger batch import for Next page"""
        if not filters:
            filters = {}
        job_options = job_options or {}
        model = self.env[self.model._name]
        if "description" not in kwargs:
            description = self.backend_record.get_queue_job_description(
                prefix=self.model.import_batch.__doc__ or "Preparing Batch Import Of",
                model=self.model._description,
            )
            job_options["description"] = description
        if not kwargs.get("no_delay"):
            model = model.with_delay(**job_options or {})
        if "identity_key" in job_options:
            job_options.pop("identity_key")
        model.import_batch(
            self.backend_record,
            filters=filters,
            force=force,
            job_options=job_options,
            **kwargs
        )


class WooDirectBatchImporter(AbstractComponent):
    """Import the records directly, without delaying the jobs."""

    _name = "woo.direct.batch.importer"
    _inherit = ["generic.direct.batch.importer", "woo.batch.importer"]


class WooDelayedBatchImporter(AbstractComponent):
    """Delay import of the records"""

    _name = "woo.delayed.batch.importer"
    _inherit = ["generic.delayed.batch.importer", "woo.batch.importer"]
