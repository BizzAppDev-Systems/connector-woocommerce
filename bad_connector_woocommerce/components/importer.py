import logging
from datetime import datetime
from copy import deepcopy
from odoo import _, fields
from odoo.exceptions import ValidationError
from odoo.addons.component.core import AbstractComponent
from odoo.addons.connector.exception import IDMissingInBackend
from odoo.addons.queue_job.exception import NothingToDoJob
from odoo.addons.queue_job.job import identity_exact

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

    def _get_remote_data(self, **kwargs):
        """Return the raw data for ``self.external_id``"""
        print("called here..... but i dont want to come here.......")
        data = self.backend_adapter.read(self.external_id)
        if not data.get(self.backend_adapter._woo_ext_id_key):
            data[self.backend_adapter._woo_ext_id_key] = self.external_id
        return data

    def _before_import(self):
        """Hook called before the import, when we have the
        data from remote system"""
        return

    def get_parsed_date(self, datetime_str):
        # TODO : Support me for the Date structure.
        return datetime_str

    def _is_uptodate(self, binding, **kwargs):
        """
        Return True if the import should be skipped because
        it is already up-to-date in OpenERP
        """
        assert self.remote_record
        if not binding:
            return  # it does not exist so it should not be skipped
        update_date = self.backend_adapter._last_update_date
        if not update_date:
            return
        last_update_date = self.remote_record.get(update_date, None)
        if not last_update_date:
            return  # no update date on WooCommerce, always import it.
        from_string = fields.Datetime.from_string
        if self.backend_adapter._check_import_sync_date:
            sync = binding.sync_date
            if not sync:
                return
        else:
            binding_update_date = self.backend_adapter._binding_update_date_field
            if not binding_update_date or (
                binding_update_date and not hasattr(binding, binding_update_date)
            ):
                return
            sync = binding[binding_update_date]
        input_date = datetime.strptime(last_update_date, "%Y-%m-%dT%H:%M:%S")
        date = input_date.strftime("%Y-%m-%d %H:%M:%S")
        remote_date = from_string(date)
        sync_date = from_string(sync)
        # if the last synchronization date is greater than the last
        # update in Woocommerce, we skip the import.
        # Important: at the beginning of the exporters flows, we have to
        # check if the last_update_date is more recent than the sync_date
        # and if so, schedule a new import. If we don't do that, we'll
        # miss changes done in Woocommerce
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
        :meth:`_import_dependency` for each dependency and handle advisory locks.

        Dependencies are related records that need to be imported before
        the main record can be successfully created or updated. This method
        iterates through the defined dependencies and imports them while
        ensuring advisory locks to prevent concurrency issues.
        """
        if not hasattr(self.backend_adapter, "_model_dependencies"):
            return
        # An advisory lock is acquired to ensure that multiple import processes
        # do not simultaneously attempt to import the same dependency, which
        # could lead to inconsistent data or conflicts. The lock name is based
        # on the backend, the main record's model, and the external ID of the
        # dependency being imported.

        # Example:
        # Suppose we are importing a product with dependencies on product categories.
        # If a product category needs to be imported for the product, this method
        # will be called to import the category. It will acquire an advisory lock
        # to prevent concurrent import processes from importing the same category.

        # In case of an advisory lock conflict, one of the processes will wait until
        # the lock is released and then proceed with the import.

        # This ensures that dependencies are imported in a controlled manner,
        # avoiding data inconsistencies and conflicts.
        for dependency in self.backend_adapter._model_dependencies:
            record = self.remote_record
            model, key = dependency
            datas = record.get(key)
            if not isinstance(datas, (list, tuple)):
                datas = [{"id": datas}]
            for data in datas:
                external_id = data.get("id")
                if not external_id:
                    continue
                lock_name = "import({}, {}, {}, {})".format(
                    self.backend_record._name,
                    self.backend_record.id,
                    model,
                    external_id,
                )
                self.advisory_lock_or_retry(lock_name)

        for dependency in self.backend_adapter._model_dependencies:
            record = self.remote_record
            model, key = dependency
            datas = record.get(key)
            if not isinstance(datas, (list, tuple)):
                datas = [{"id": datas}]
            for data in datas:
                external_id = data.get("id")
                if not external_id:
                    continue
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
        # binder = self.binder_for(model="woo.sale.order")
        # sale_order = binder.to_internal(self.remote_record.get("order_id"), unwrap=True)
        # delivery_order = sale_order.picking_ids[0]
        # # T-02039 Create the wizard for return based on the delivery order.
        # return_wizard = (
        #     self.env["stock.return.picking"]
        #     .with_context(active_id=delivery_order.id, active_model="stock.picking")
        #     .new({})
        # )
        # return_wizard._onchange_picking_id()
        # binder = self.binder_for(model="woo.product.product")

        # # Group by qty based on product id
        # product_grouped_qty = {}
        # product_return_qty = {}
        # for line in self.remote_record.get("line_items"):
        #     quantity = abs(line.get("quantity"))
        #     product_id = binder.to_internal(line.get("product_id"), unwrap=True).id
        #     if product_id not in product_grouped_qty:
        #         product_grouped_qty[product_id] = 0
        #     product_grouped_qty[product_id] += quantity
        #     if product_id not in product_return_qty:
        #         product_return_qty[product_id] = []
        #     product_return_qty[product_id].append(
        #         [line.get("id"), quantity]
        #     )
        # print(product_grouped_qty, product_return_qty,"plllllllllllppppppppppppppp")
        # for item in self.remote_record.get("line_items"):
        #     product_id = binder.to_internal(item.get("product_id"), unwrap=True).id
        #     return_line = return_wizard.product_return_moves.filtered(
        #         lambda r: r.product_id.id == product_id
        #     )
        #     # T-02039 move_external_id does have a value of external_id of moves and
        #     # update quantity set the external id for move.
        #     return_line.update(
        #         {
        #             "quantity": float(product_grouped_qty[product_id]),
        #         }
        #     )
        # picking_returns = return_wizard._convert_to_write(
        #     {name: return_wizard[name] for name in return_wizard._cache}
        # )
        # moves = [(6, 0, [])]
        # for returns in picking_returns["product_return_moves"]:
        #     if returns[-1] and "move_external_id" in list(returns[-1].keys()):
        #         product_id = returns[-1]["product_id"]
        #         for group_return in product_return_qty[product_id]:
        #             line_id, qty = group_return
        #             new_return = deepcopy(returns)
        #             new_return[-1].update(
        #                 {"quantity": qty, "move_external_id": line_id}
        #             )
        #             moves.append(new_return)
        # picking_returns["product_return_moves"] = moves
        # T-02039 creates return for the picking with the moves.
        # stock_return_picking = (
        #     self.env["stock.return.picking"]
        #     .with_context(do_not_merge=True)
        #     .create(picking_returns)
        # )
        # print(stock_return_picking, "pppppppppsssssssssssssmmmmmmmmmmmmmm")
        # return_id, return_type = stock_return_picking._create_returns()
        # data["odoo_id"] = return_id
        # picking_id = self.env["stock.picking"].browse(return_id)
        # print(picking_id, "lplplplplplplpl")
        # for item in data.get("everstox_stock_move_out_ids"):
        #     external_id = item[-1].get("external_id")
        #     stock_move = picking_id.move_lines.filtered(
        #         lambda m: m.external_move == external_id
        #     )
        #     item[-1]["odoo_id"] = stock_move.id

        #     # Logic to set scrap location in case of defect
        #     return_status = item[-1]["everstox_return_stock_state_id"]
        #     item[-1]["everstox_return_stock_state_id"] = return_status.id
        #     # If not scappable state then continue
        #     if not return_status.consider_scrap:
        #         continue
        #     # Get scrap location from backend
        #     scrap_location = self.backend_record.scrap_location_id
        #     # if not scrap_location:
        #     #     raise MappingError(_("Please select scrap location in Backend!"))

        #     # set scrap location as destination location
        #     item[-1]["location_dest_id"] = scrap_location.id

        # res = super(EverstoxStockPickingOutReturnImporter, self)._create(data)
        # T-02039- Filters the moves to create activity.
        # moves = res.everstox_stock_move_out_ids.filtered(
        #     lambda r: not r.everstox_return_reason or not r.everstox_return_reason_code
        # )
        # # T-02039 Creates the activity for the reason and reason code based on the condition.
        # message = ""
        # for move in res.everstox_stock_move_out_ids:
        #     if move.everstox_return_reason_code and not move.everstox_return_reason:
        #         message += (
        #             "Move: %s(%s): Return Reason is missing for the reason code %s\n"
        #         ) % (
        #             move.odoo_id.id,
        #             move.product_id.name,
        #             move.everstox_return_reason_code,
        #         )
        #     elif (
        #         not move.everstox_return_reason_code and not move.everstox_return_reason
        #     ):
        #         message += (
        #             "Move: %s(%s): Return Reason and Reason code both are missing"
        #         ) % (move.odoo_id.id, move.product_id.name)
        # if message:
        #     self.env["everstox.backend"].create_activity(
        #         record=res.odoo_id,
        #         message=message,
        #         activity_type="connector_settings.mail_activity_data_warning",
        #         user=self.backend_record.activity_user_id,
        #     )
        # return res
        # print(
        #     picking_returns,
        #     "ssssssssssssssssssssssssssssssss picking_returnspicking_returns",
        # )
        # print("importer create method")
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

    def run(self, external_id, data=None, force=False, **kwargs):
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
        if force:
            kwargs["force"] = force
        if data and "return" not in kwargs:
            self.remote_record = data
        else:
            try:
                print(kwargs, "ppppppppppp kwargskwargskwargskwargskwargskwargs")
                self.remote_record = self._get_remote_data(**kwargs)
                print("hereeeeeeeeeeeeeeeeeeeeeee after _get_remote_data")
            except IDMissingInBackend:
                return _("Record does no longer exist in remote system")

        skip = self._must_skip()  # pylint: disable=assignment-from-none
        if skip:
            return skip
        binding = self._get_binding()
        if not force and self._is_uptodate(binding, **kwargs):
            return _("Already up-to-date.")
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
            print(binding, "binding binding binding binding")
        self.binder.bind(self.external_id, binding)
        self._after_import(binding, **kwargs)


class WooMapChildImport(AbstractComponent):
    _name = "woo.map.child.import"
    _inherit = ["connector.woo.base", "base.map.child.import"]
    _usage = "import.map.child"

    def format_items(self, items_values):
        """Format the values of the items mapped from the child Mappers.

        It can be overridden for instance to add the Odoo
        relationships commands ``(6, 0, [IDs])``, ...

        As instance, it can be modified to handle update of existing
        items: check if an 'id' has been defined by
        :py:meth:`get_item_values` then use the ``(1, ID, {values}``)
        command

        :param items_values: list of values for the items to create
        :type items_values: list

        """
        final_vals = []
        for item in items_values:
            external_id = item["external_id"]
            binder = self.binder_for(model=self.model)
            binding = binder.to_internal(external_id)
            if binding:
                final_vals.append((1, binding.id, item))  # update
            else:
                final_vals.append((0, 0, item))  # create
        return final_vals


class WooBatchImporter(AbstractComponent):
    """
    The role of a BatchImporter is to search for a list of
    items to import, then it can either import them directly or delay
    the import of each item separately.
    """

    _name = "woo.batch.importer"
    _inherit = ["base.importer", "connector.woo.base"]
    _usage = "batch.importer"

    def run(self, filters=None, force=None, job_options=None, **kwargs):
        """Run the synchronization"""
        if force:
            kwargs["force"] = force
        filters = filters or {}
        if "record_count" not in filters:
            filters.update({"record_count": 0})
        data = self.backend_adapter.search(filters)
        records = data.get("data", [])
        for record in records:
            external_id = record.get(self.backend_adapter._woo_ext_id_key)
            self._import_record(external_id, job_options, data=record, **kwargs)
        filters["record_count"] += len(records)
        record_count = data.get("record_count", 0)
        filters_record_count = filters.get("record_count", 0)
        if (
            record_count is not None
            and filters_record_count is not None
            and int(record_count) > int(filters_record_count)
        ):
            filters.update({"page": filters.get("page", 1) + 1})
            self.process_next_page(filters=filters, job_options=job_options, **kwargs)

    def process_next_page(self, filters=None, job_options=None, **kwargs):
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
        model.import_batch(
            self.backend_record, filters=filters, job_options=job_options, **kwargs
        )

    def _import_record(self, external_id, job_options=None, data=None, **kwargs):
        """
        Import a record directly or delay the import of the record.
        Method to implement in sub-classes.
        """
        raise NotImplementedError


class WooDirectBatchImporter(AbstractComponent):
    """Import the records directly, without delaying the jobs."""

    _name = "woo.direct.batch.importer"
    _inherit = "woo.batch.importer"

    def _import_record(self, external_id, data=None, force=None, **kwargs):
        """Import the record directly"""
        self.model.import_record(
            self.backend_record,
            external_id=external_id,
            data=data,
            force=force,
            **kwargs
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
        if "description" not in kwargs:
            description = self.backend_record.get_queue_job_description(
                prefix=self.model.import_record.__doc__ or "Record Import Of",
                model=self.model._description,
            )
            job_options["description"] = description
        delayable = self.model.with_delay(**job_options or {})
        delayable.import_record(self.backend_record, external_id, data=data, **kwargs)
