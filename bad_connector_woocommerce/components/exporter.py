"""

Exporters for woo.

In addition to its export job, an exporter has to:

* check in woo if the record has been updated more recently than the
  last sync date and if yes, delay an import
* call the ``bind`` method of the binder to update the last sync date

"""

import logging

from odoo.addons.component.core import AbstractComponent

_logger = logging.getLogger(__name__)


class WooExporter(AbstractComponent):
    """A common flow for the exports to woocommerce"""

    _name = "woo.exporter"
    _inherit = ["generic.base.exporter", "connector.woo.base"]
    _usage = "record.exporter"
    # _default_binding_field = "woo_bind_ids"

    # def __init__(self, work_context):
    #     super(WooExporter, self).__init__(work_context)
    #     self.binding = None
    #     self.external_id = None
    #     # save response, so that we can use it in after complete to import
    #     # the latest status in odoo instead of sending the import request again
    #     self.response_data = None
    #     self.remote_record = None

    # def _should_import(self, **kwargs):
    #     if not self.binding:
    #         return True
    #     return False

    # def create_get_binding(self, record, extra_data=None, **kwargs):
    #     """Search for the existing binding else create new binding"""
    #     binder = self.binder_for(model=self.model._name)
    #     external_id = False
    #     if self._default_binding_field and record[self._default_binding_field]:
    #         binding = record[self._default_binding_field][:1]
    #         external_id = binding[self.backend_adapter._odoo_ext_id_key]

    #     binding = False
    #     if external_id:
    #         binding = binder.to_internal(external_id, unwrap=False)
    #     if not binding:
    #         binding = self.model.search(
    #             [
    #                 ("odoo_id", "=", record.id),
    #                 ("external_id", "=", False),
    #                 ("backend_id", "=", self.backend_record.id),
    #             ],
    #             limit=1,
    #         )
    #     if not binding:
    #         # create new binding
    #         data = {}
    #         if extra_data and isinstance(extra_data, dict):
    #             data.update(extra_data)
    #         data.update(
    #             {
    #                 "odoo_id": record.id,
    #                 "external_id": False,
    #                 "backend_id": self.backend_record.id,
    #             }
    #         )
    #         binding = self.model.create(data)
    #     return binding

    # def run(self, binding, record=None, *args, **kwargs):
    #     """
    #     Run the synchronization
    #     :param binding: binding record to export
    #     """
    #     if not binding:
    #         if not record:
    #             raise ValidationError(_("No record found to export!!!"))
    #         binding = self.create_get_binding(record, **kwargs)

    #     self.binding = binding
    #     self.external_id = self.binder.to_external(self.binding)
    #     try:
    #         should_import = self._should_import()
    #     except IDMissingInBackend:
    #         self.external_id = None
    #         should_import = False
    #     if should_import:
    #         self._delay_import()
    #         return

    #     result = self._run(*args, **kwargs)
    #     if not self.external_id or self.external_id == "False":
    #         self.external_id = record.id
    #     self.binder.bind(self.external_id, self.binding)
    #     # Commit so we keep the external ID when there are several
    #     # exports (due to dependencies) and one of them fails.
    #     # The commit will also release the lock acquired on the binding
    #     # record
    #     if not tools.config["test_enable"]:
    #         self.env.cr.commit()  # pylint: disable=E8102
    #     self._after_export(self.binding)
    #     return result

    # def _lock(self):
    #     """Lock the binding record.

    #     Lock the binding record so we are sure that only one export
    #     job is running for this record if concurrent jobs have to export the
    #     same record.

    #     When concurrent jobs try to export the same record, the first one
    #     will lock and proceed, the others will fail to lock and will be
    #     retried later.

    #     This behavior works also when the export becomes multilevel
    #     with :meth:`_export_dependencies`. Each level will set its own lock
    #     on the binding record it has to export.

    #     """
    #     sql = "SELECT id FROM %s WHERE ID = %%s FOR UPDATE NOWAIT" % self.model._table
    #     try:
    #         self.env.cr.execute(sql, (self.binding.id,), log_exceptions=False)
    #     except psycopg2.OperationalError:
    #         _logger.info(
    #             "A concurrent job is already exporting the same "
    #             "record (%s with id %s). Job delayed later.",
    #             self.model._name,
    #             self.binding.id,
    #         )
    #         raise RetryableJobError(
    #             "A concurrent job is already exporting the same record "
    #             "(%s with id %s). The job will be retried later."
    #             % (self.model._name, self.binding.id)
    #         )

    # def _after_export(self):
    #     pass

    # def _export_dependency(
    #     self,
    #     relation,
    #     binding_model,
    #     component_usage="record.exporter",
    #     binding_field=None,
    #     binding_extra_vals=None,
    #     **kwargs,
    # ):
    #     exporter = self.component(usage=component_usage, model_name=binding_model)
    #     # Call importer if we need to import record in dependency
    #     if component_usage == "record.importer":
    #         external_id = None
    #         if (
    #             exporter._default_binding_field
    #             and relation[exporter._default_binding_field]
    #         ):
    #             binding = relation[exporter._default_binding_field][:1]
    #             external_id = binding[exporter.backend_adapter._odoo_ext_id_key]
    #         # can't proceed with single record import
    #         # if external if is missing
    #         if not external_id:
    #             raise ValidationError(
    #                 _(
    #                     "Failed export!!! Dependency missing!!! Please initiate"
    #                     " the import of record %s"
    #                 )
    #                 % (relation)
    #             )
    #         return exporter._import_dependency(
    #             external_id=external_id, binding_model=binding_model
    #         )

    #     # if record is already exported, then no need to export again
    #     if binding_field is None:
    #         binding_field = exporter._default_binding_field

    #     binding_ids = getattr(relation, binding_field)
    #     binder = self.binder_for(binding_model)
    #     if binding_ids.filtered(
    #         lambda bind: getattr(bind, binder._external_field)
    #         and bind.backend_id == self.backend_record
    #     ):
    #         return

    #     if not relation:
    #         return
    #     # wrap is typically True if the relation is for instance a
    #     # 'res.partner' record but the binding model is
    #     # 'my_bakend.res.partner'
    #     wrap = relation._name != binding_model

    #     if wrap and hasattr(relation, binding_field):
    #         domain = [
    #             ("odoo_id", "=", relation.id),
    #             ("backend_id", "=", self.backend_record.id),
    #         ]
    #         binding = self.env[binding_model].search(domain)
    #         if binding:
    #             assert len(binding) == 1, (
    #                 "only 1 binding for a backend is " "supported in _export_dependency"
    #             )
    #         # we are working with a unwrapped record (e.g.
    #         # product.category) and the binding does not exist yet.
    #         # Example: I created a product.product and its binding
    #         # my_backend.product.product and we are exporting it, but we need
    #         # to create the binding for the product.category on which it
    #         # depends.
    #         else:
    #             # BAD customization: moved to create_get_binding
    #             with self._retry_unique_violation():
    #                 binding = exporter.create_get_binding(
    #                     record=relation, extra_data=binding_extra_vals, **kwargs
    #                 )
    #                 # BAD customization end
    #                 if not tools.config["test_enable"]:
    #                     self.env.cr.commit()  # pylint: disable=E8102
    #     else:
    #         # If my_backend_bind_ids does not exist we are typically in a
    #         # "direct" binding (the binding record is the same record).
    #         # If wrap is True, relation is already a binding record.
    #         binding = relation

    #     if not binder.to_external(binding):
    #         exporter.run(binding, **kwargs)

    # def _before_export(self, **kwargs):
    #     pass

    # def _export_dependencies(self, **kwargs):
    #     """
    #     Import the dependencies for the record

    #     Import of dependencies can be done manually or by calling
    #     :meth:`_import_dependency` for each dependency.
    #     """
    #     if not hasattr(self.backend_adapter, "_model_export_dependencies"):
    #         return
    #     record = self.binding.odoo_id
    #     for dependency in self.backend_adapter._model_export_dependencies:
    #         model, key = dependency
    #         relations = record.mapped(key)
    #         for relation in relations:
    #             self._export_dependency(
    #                 relation=relation,
    #                 binding_model=model,
    #             )

    # def _run(self, binding, fields=None, **kwargs):
    #     """Flow of the synchronization, implemented in inherited classes"""
    #     assert self.binding

    #     if not self.external_id:
    #         fields = None  # should be created with all the fields

    #     self._before_export()
    #     # export the missing linked resources
    #     self._export_dependencies()

    #     # prevent other jobs to export the same record
    #     # will be released on commit (or rollback)
    #     self._lock()
    #     map_record = self._map_data()
    #     if self.external_id:
    #         record = self._update_data(map_record, fields=fields)
    #         if not record:
    #             return _("Nothing to export.")
    #         self._update(record)
    #     else:
    #         record = self._create_data(map_record, fields=fields)
    #         if not record:
    #             return _("Nothing to export.")
    #         res = self._create(record)
    #         # BAD start
    #         if isinstance(res, dict):
    #             # add logger error in case of not getting proper data while exporting
    #             # partners
    #             if self.backend_adapter._woo_ext_id_key not in res:
    #                 _logger.error("Error while exporting partner: %s", res)
    #             else:
    #                 self.external_id = res.get(self.backend_adapter._woo_ext_id_key)
    #                 self.response_data = res
    #         else:
    #             # added None explicitly as in case of False it adds the external id
    #             # as "False", and raise no error.
    #             self.external_id = (
    #                 self.binding[self.backend_adapter._odoo_ext_id_key] or None
    #             )
    #         # BAD end
    #     return _("Record exported with ID %s on Backend.") % self.external_id


class WooBatchExporter(AbstractComponent):
    """
    The role of a BatchExporter is to search for a list of
    items to export, then it can either export them directly or delay
    the export of each item separately.
    """

    _name = "woo.batch.exporter"
    _inherit = ["generic.batch.exporter", "connector.woo.base"]
    _usage = "batch.exporter"

    # def run(self, filters=None, fields=None, job_options=None, **kwargs):
    #     """Run the synchronization"""
    #     records = self.backend_adapter.search(filters)
    #     for record in records:
    #         self._export_record(record, fields, job_options, **kwargs)

    # def _export_record(self, record, fields=None, job_options=None, **kwargs):
    #     """
    #     Export a record directly or delay the export of the record.

    #     Method to implement in sub-classes.
    #     """
    #     # self.model.export_record(self.backend_record, record)
    #     raise NotImplementedError


class WooDirectBatchExporter(AbstractComponent):
    """Export the records directly, without delaying the jobs."""

    _name = "woo.direct.batch.exporter"
    _inherit = "generic.direct.batch.exporter"

    # def _export_record(self, record, fields=None, job_options=None, **kwargs):
    #     """Delay the export of the records"""
    #     job_options = job_options or {}
    #     if "identity_key" not in job_options:
    #         job_options["identity_key"] = identity_exact
    #     if "description" in job_options:
    #         description = self.backend_record.get_queue_job_description(
    #             prefix=self.model.export_record.__doc__ or "Record Export Of",
    #             model=self.model._description,
    #         )
    #         job_options["description"] = description
    #     delayable = self.model.with_delay(**job_options or {})
    #     delayable.export_record(self.backend_record, record, fields, **kwargs)


class WooDelayedBatchExporter(AbstractComponent):
    """Delay export of the records"""

    _name = "woo.delayed.batch.exporter"
    _inherit = "generic.delayed.batch.exporter"

    # def _export_record(self, record, fields, job_options=None, **kwargs):
    #     """Delay the export of the records"""
    #     job_options = job_options or {}
    #     if "identity_key" not in job_options:
    #         job_options["identity_key"] = identity_exact
    #     if "description" in job_options:
    #         description = self.backend_record.get_queue_job_description(
    #             prefix=self.model.export_record.__doc__ or "Record Export Of",
    #             model=self.model._description,
    #         )
    #         job_options["description"] = description
    #     delayable = self.model.with_delay(**job_options or {})
    #     delayable.export_record(self.backend_record, record, fields=fields, **kwargs)
