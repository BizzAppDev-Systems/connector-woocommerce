import logging

from odoo import _, fields
from odoo.exceptions import ValidationError

from odoo.addons.component.core import AbstractComponent
from odoo.addons.connector.exception import IDMissingInBackend
from odoo.addons.queue_job.exception import NothingToDoJob
from odoo.addons.queue_job.job import identity_exact

from .misc import get_queue_job_description

_logger = logging.getLogger(__name__)


class WooImporter(AbstractComponent):
    """Base importer for woocommerce"""

    _name = "woo.importer"
    _inherit = ["base.importer", "connector.woo.base"]
    _usage = "record.importer"

    def __init__(self, work_context):
        super(WooImporter, self).__init__(work_context)
        self.binding = None
        self.external_id = None
        self.remote_record = None

    def _get_remote_data(self):
        """Return the raw data for ``self.external_id``"""
        data = self.backend_adapter.read(self.external_id)
        if not data.get(self.backend_adapter._woo_ext_id_key):
            data[self.backend_adapter._woo_ext_id_key] = self.external_id
        return data

    def _before_import(self):
        """Hook called before the import, when we have the
        data from remote system"""

    def get_parsed_date(self, datetime_str):
        # TODO : Support me for the Date structure.
        return datetime_str

    def _is_uptodate(self, binding):
        """Return True if the import should be skipped because
        it is already up-to-date in OpenERP"""
        update_field = self.backend_adapter._last_update_field
        if not update_field:
            return
        assert self.remote_record
        if not self.remote_record.get(update_field):
            return  # no update date on remote system, always import it.
        if not binding:
            return  # it does not exist so it should not be skipped
        sync = binding.sync_date
        if not sync:
            return
        from_string = fields.Datetime.from_string
        sync_date = from_string(sync)
        remote_date = self.get_parsed_date(self.remote_record[update_field])
        # if the last synchronization date is greater than the last
        # update in remote, we skip the import.
        # Important: at the beginning of the exporters flows, we have to
        # check if the remote_date is more recent than the sync_date
        # and if so, schedule a new import. If we don't do that, we'll
        # miss changes done in remote system
        return remote_date < sync_date

    def _import_dependency(
        self, external_id, binding_model, importer=None, always=False
    ):
        """
        Import a dependency.
        The importer class is a class or subclass of
        :class:`GenericImporter`. A specific class can be defined.

        :param external_id: id of the related binding to import
        :param binding_model: name of the binding model for the relation
        :type binding_model: str | unicode
        :param importer_component: component to use for import
                                   By default: 'importer'
        :type importer_component: Component
        :param always: if True, the record is updated even if it already
                       exists, note that it is still skipped if it has
                       not been modified on remote system since the last
                       update. When False, it will import it only when
                       it does not yet exist.
        :type always: boolean
        """
        if not external_id:
            return
        binder = self.binder_for(binding_model)
        if always or not binder.to_internal(external_id):
            if importer is None:
                importer = self.component(
                    usage="record.importer", model_name=binding_model
                )
            try:
                importer.run(external_id)
            except NothingToDoJob:
                _logger.info(
                    "Dependency import of %s(%s) has been ignored.",
                    binding_model._name,
                    external_id,
                )

    def _import_dependencies(self):
        """
        Import the dependencies for the record
        Import of dependencies can be done manually or by calling
        :meth:`_import_dependency` for each dependency.
        """
        if not hasattr(self.backend_adapter, "_model_dependencies"):
            return
        for dependency in self.backend_adapter._model_dependencies:
            record = self.remote_record
            model, key = dependency
            external_id = record.get(key)
            self._import_dependency(external_id=external_id, binding_model=model)

    def _map_data(self):
        """
        Returns an instance of
        :py:class:`~odoo.addons.connector.components.mapper.MapRecord`
        """
        return self.mapper.map_record(self.remote_record)

    def _validate_data(self, data):
        """Check if the values to import are correct

        Pro-actively check before the ``_create`` or
        ``_update`` if some fields are missing or invalid.

        Raise `InvalidDataError`
        """
        return

    def _must_skip(self):
        """
        Hook called right after we read the data from the backend.

        If the method returns a message giving a reason for the
        skipping, the import will be interrupted and the message
        recorded in the job (if the import is called directly by the
        job, not by dependencies).

        If it returns None, the import will continue normally.

        :returns: None | str | unicode
        """
        return

    def _get_binding(self):
        return self.binder.to_internal(self.external_id)

    def _create_data(self, map_record, **kwargs):
        return map_record.values(for_create=True, **kwargs)

    def _create(self, data):
        """Create the OpenERP record"""
        # special check on data before import
        self._validate_data(data)
        model = self.model.with_context(connector_no_export=True)
        binding = model.create(data)
        _logger.debug("%d created from remote system %s", binding, self.external_id)
        return binding

    def _update_data(self, map_record, **kwargs):
        return map_record.values(**kwargs)

    def _update(self, binding, data):
        """Update an OpenERP record"""
        # special check on data before import
        self._validate_data(data)
        binding.with_context(connector_no_export=True).write(data)
        _logger.debug("%d updated from remote system %s", binding, self.external_id)
        return

    def _after_import(self, binding, **kwargs):
        """Hook called at the end of the import"""
        return

    def run(self, external_id, data=None, force=False):
        """Run the synchronization

        :param external_id: identifier of the record on remote system
        """
        self.external_id = external_id
        lock_name = "import({}, {}, {}, {})".format(
            self.backend_record._name,
            self.backend_record.id,
            self.work.model_name,
            external_id,
        )
        if data:
            self.remote_record = data
        else:
            try:
                self.remote_record = self._get_remote_data()
            except IDMissingInBackend:
                return _("Record does no longer exist in remote system")

        skip = self._must_skip()  # pylint: disable=assignment-from-none
        if skip:
            return skip
        binding = self._get_binding()

        # Keep a lock on this import until the transaction is committed
        # The lock is kept since we have detected that the information
        # will be updated into Odoo
        self.advisory_lock_or_retry(lock_name)
        self._before_import()

        # import the missing linked resources
        self._import_dependencies()

        map_record = self._map_data()
        if binding:
            record = self._update_data(map_record)
            self._update(binding, record)
        else:
            record = self._create_data(map_record)
            binding = self._create(record)
        self.binder.bind(self.external_id, binding)


class WooMapChildImport(AbstractComponent):
    _name = "woo.map.child.import"
    _inherit = ["connector.woo.base", "base.map.child.import"]
    _usage = "import.map.child"


class WooBatchImporter(AbstractComponent):
    """
    The role of a BatchImporter is to search for a list of
    items to import, then it can either import them directly or delay
    the import of each item separately.
    """

    _name = "woo.batch.importer"
    _inherit = ["base.importer", "connector.woo.base"]
    _usage = "batch.importer"

    def run(self, filters=None, force=None, **kwargs):
        """Run the synchronization"""
        filters = filters or {}
        try:
            records = self.backend_adapter.search(filters)
            for record in records:
                external_id = record.get(self.backend_adapter._woo_ext_id_key)
                self._import_record(external_id, data=record)
            if records:
                filters.update({"page": filters.get("page", 1) + 1})
                self.process_next_page(filters)
        except Exception as err:
            raise ValidationError(_("Error : %s") % err) from err

    def _import_record(self, external_id, job_options=None, data=None, **kwargs):
        """
        Import a record directly or delay the import of the record.
        Method to implement in sub-classes.
        """
        job_options = job_options or {}
        if "identity_key" not in job_options:
            job_options["identity_key"] = identity_exact
        job_options["description"] = get_queue_job_description(
            model_name=self.model._name, job_type="Import"
        )
        delayable = self.model.with_delay(**job_options or {})
        delayable.import_record(self.backend_record, external_id, data=data, **kwargs)

    def process_next_page(self, filters=None, job_options=None, **kwargs):
        """Method to trigger batch import for Next page"""
        if not filters:
            filters = {}
        job_options = job_options or {}
        model = self.env[self.model._name]
        if not kwargs.get("no_delay"):
            model = model.with_delay(**job_options or {})
        model.import_batch(
            self.backend_record, filters=filters, job_options=job_options, **kwargs
        )


class WooDirectBatchImporter(AbstractComponent):
    """Import the records directly, without delaying the jobs."""

    _name = "woo.direct.batch.importer"
    _inherit = "woo.batch.importer"

    def _import_record(self, external_id, data=None, force=None):
        """Import the record directly"""
        self.model.import_record(
            self.backend_record, external_id=external_id, data=data, force=force
        )


class WooDelayedBatchImporter(AbstractComponent):
    """Delay import of the records"""

    _name = "woo.delayed.batch.importer"
    _inherit = "woo.batch.importer"

    def _import_record(self, external_id, job_options=None, data=None, **kwargs):
        """Delay the import of the records"""
        job_options = job_options or {}
        if "identity_key" not in job_options:
            job_options["identity_key"] = identity_exact
        delayable = self.model.with_delay(**job_options or {})
        delayable.import_record(self.backend_record, external_id, data=data, **kwargs)
