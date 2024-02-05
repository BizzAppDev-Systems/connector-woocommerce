import json
from copy import deepcopy

from odoo import _, fields
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from odoo.addons.connector.exception import MappingError
from odoo.addons.connector_warehouse.components.misc import from_iso_datetime


class WooStockPickingOutReturnImportMapper(Component):
    _name = "woo.stock.picking.out.return.import.mapper"
    _inherit = "woo.refund.import.mapper"
    _apply_on = "woo.stock.picking.out.return"
    _map_child_fallback = "woo.map.child.import"

    direct = [("id", "external_id")]

    children = [
        (
            "return_items",
            "woo_stock_move_out_ids",
            "woo.stock.move.out.return",
        ),
    ]

    def get_picking(self, record):
        """#T-02039 returns the DO."""
        binder = self.binder_for(model="woo.stock.picking.out")
        order = binder.to_internal(record.get("order").get("id"), unwrap=True)
        if not order:
            raise MappingError(
                _(
                    "No delivery order found with external id %s"
                    % (record.get("order").get("id"))
                )
            )
        return order

    def get_picking_return(self, record):
        """#T-02039 returns the return of picking"""
        binder = self.binder_for(model="woo.stock.picking.out.return")
        return_id = binder.to_internal(record.get("id"), unwrap=True)
        return return_id

    @mapping
    def rma_num(self, record):
        """Mapping of rma_num"""
        rma_num = record.get("rma_num") or ""
        return {"carrier_tracking_ref": rma_num}

    @mapping
    def backend_id(self, record):
        """Mapping of backend_id"""
        return {"backend_id": self.backend_record.id}

    @mapping
    def woo_data(self, record):
        """Return woo data."""
        return {"woo_data": json.dumps(record, indent=2)}

    @mapping
    def set_picking_options(self, record):
        """
        #T-02039 Dummy method:just to add the picking record in options so that
        we can get it's value in child mapper options
        """
        picking_return = self.get_picking_return(record)
        self.options.update(picking_id=picking_return.id)
        return {}

    @mapping
    def return_date(self, record):
        """#T-02039 Mapping for the return_date."""
        return_date = record.get("return_date")
        if not return_date:
            return {}
        return {"woo_return_date": from_iso_datetime(return_date)}

    @mapping
    def updated_date(self, record):
        """#T-02039 Mapping for the updated_date."""
        updated_date = record.get("updated_date")
        if not updated_date:
            return {}
        return {"woo_return_updated_date": from_iso_datetime(updated_date)}

    @mapping
    def z_everstox_return_status(self, record):
        """
        #T-02039 Started this method name with z in order to make sure this would be last
        field to be write on picking. (connector call all mapping methods in
        alphabetical order).
        Reason: there is series of write calls (to add data in parent
        record(stock.picking) from create/write of binding(everstox.stock.picking))
        and in between these calls, value of status fields actually gets lost.
        and nothing write down in status (don't know exact reason, it is because cache
        is clearing from somewhere or something else, but this is solving the issue)
        """
        status = record.get("state").upper()
        status_id = self.env["remote.shipment.status"].search(
            [("name", "=", status), ("status_type", "=", "return")],
            order="sequence",
            limit=1,
        )
        if not status_id:
            status_id = self.env["remote.shipment.status"].create(
                {"name": status, "status_type": "return"}
            )
        everstox_status_date = fields.Date.today()
        # T-02039 Prepare the dictionary for the remote.shipment.status
        status_dict = {
            "status_id": status_id.id,
            "sequence": status_id.sequence,
            "occured_at": everstox_status_date,
        }
        everstox_status_ids = [(0, 0, status_dict)]
        picking_return = self.get_picking_return(record)
        res = {
            "everstox_return_status_id": status_id.id,
            "status_date": everstox_status_date,
            "status_history_ids": everstox_status_ids,
        }
        if not picking_return:
            return res
        # T-02039 returns empty if return status is already created.
        picking_status_list = picking_return.status_history_ids.mapped("status_id")
        if status_id == picking_return.status_id or status_id in picking_status_list:
            return {}
        return res


class WooStockPickingOutReturnImporter(Component):
    _name = "woo.stock.picking.out.return.importer"
    _inherit = "woo.refund.importer"
    _apply_on = "woo.stock.picking.out.return"
    _default_binding_field = "woo_out_return_bind_ids"

    def _must_skip(self):
        """#T-02159 Skip the return if already binding exists."""
        if self.binder.to_internal(self.external_id):
            return True
        return super(WooStockPickingOutReturnImporter, self)._must_skip()

    def _create(self, data):
        """# T-02039 inherit the method create lines of return"""
        binder = self.binder_for(model="woo.stock.picking.out")
        delivery_order = binder.to_internal(
            self.remote_record.get("order").get("id"), unwrap=True
        )
        # T-02039 Create the wizard for return based on the delivery order.
        return_wizard = (
            self.env["stock.return.picking"]
            .with_context(active_id=delivery_order.id, active_model="stock.picking")
            .new({})
        )
        return_wizard._onchange_picking_id()
        binder = self.binder_for(model="woo.product.product")

        # Group by qty based on product id
        product_grouped_qty = {}
        product_return_qty = {}
        for line in self.remote_record.get("return_items"):
            product_id = binder.to_internal(
                line.get("product").get("id"), unwrap=True
            ).id
            if product_id not in product_grouped_qty:
                product_grouped_qty[product_id] = 0
            product_grouped_qty[product_id] += line.get("quantity")
            if product_id not in product_return_qty:
                product_return_qty[product_id] = []
            product_return_qty[product_id].append(
                [line.get("id"), line.get("quantity")]
            )

        # T-02039 Prepare the moves based on the values for the return.
        for item in self.remote_record.get("return_items"):
            product_id = binder.to_internal(
                item.get("product").get("id"), unwrap=True
            ).id
            return_line = return_wizard.product_return_moves.filtered(
                lambda r: r.product_id.id == product_id
            )
            # T-02039 move_external_id does have a value of external_id of moves and
            # update quantity set the external id for move.
            return_line.update(
                {
                    "quantity": float(product_grouped_qty[product_id]),
                    "move_external_id": item.get("id"),
                }
            )
        # T-02039 Write the values from cache of return_wizard.
        picking_returns = return_wizard._convert_to_write(
            {name: return_wizard[name] for name in return_wizard._cache}
        )
        moves = [(6, 0, [])]
        # T-02039 Remove lines which doesn't have move_external_id.
        for returns in picking_returns["product_return_moves"]:
            if returns[-1] and "move_external_id" in list(returns[-1].keys()):
                product_id = returns[-1]["product_id"]
                for group_return in product_return_qty[product_id]:
                    line_id, qty = group_return
                    new_return = deepcopy(returns)
                    new_return[-1].update(
                        {"quantity": qty, "move_external_id": line_id}
                    )
                    moves.append(new_return)
        picking_returns["product_return_moves"] = moves
        # T-02039 creates return for the picking with the moves.
        stock_return_picking = (
            self.env["stock.return.picking"]
            .with_context(do_not_merge=True)
            .create(picking_returns)
        )
        return_id, return_type = stock_return_picking._create_returns()
        data["odoo_id"] = return_id
        picking_id = self.env["stock.picking"].browse(return_id)
        for item in data.get("everstox_stock_move_out_ids"):
            external_id = item[-1].get("external_id")
            stock_move = picking_id.move_lines.filtered(
                lambda m: m.external_move == external_id
            )
            item[-1]["odoo_id"] = stock_move.id

            # Logic to set scrap location in case of defect
            return_status = item[-1]["everstox_return_stock_state_id"]
            item[-1]["everstox_return_stock_state_id"] = return_status.id
            # If not scappable state then continue
            if not return_status.consider_scrap:
                continue
            # Get scrap location from backend
            scrap_location = self.backend_record.scrap_location_id
            if not scrap_location:
                raise MappingError(_("Please select scrap location in Backend!"))

            # set scrap location as destination location
            item[-1]["location_dest_id"] = scrap_location.id

        res = super(WooStockPickingOutReturnImporter, self)._create(data)
        # T-02039- Filters the moves to create activity.
        moves = res.everstox_stock_move_out_ids.filtered(
            lambda r: not r.everstox_return_reason or not r.everstox_return_reason_code
        )
        # T-02039 Creates the activity for the reason and reason code based on the condition.
        message = ""
        for move in res.everstox_stock_move_out_ids:
            if move.everstox_return_reason_code and not move.everstox_return_reason:
                message += (
                    "Move: %s(%s): Return Reason is missing for the reason code %s\n"
                ) % (
                    move.odoo_id.id,
                    move.product_id.name,
                    move.everstox_return_reason_code,
                )
            elif (
                not move.everstox_return_reason_code and not move.everstox_return_reason
            ):
                message += (
                    "Move: %s(%s): Return Reason and Reason code both are missing"
                ) % (move.odoo_id.id, move.product_id.name)
        if message:
            self.env["everstox.backend"].create_activity(
                record=res.odoo_id,
                message=message,
                activity_type="connector_settings.mail_activity_data_warning",
                user=self.backend_record.activity_user_id,
            )
        return res

    def _after_import(self, binding, **kwargs):
        """#T-02039 create the move lines and lots"""
        picking = binding.odoo_id
        for move_bind in binding.everstox_stock_move_out_ids:
            move = move_bind.odoo_id
            if move.product_id.tracking == "none":
                move.quantity_done = move_bind.return_qty
                continue
            move.move_line_ids.unlink()
            move_line_ids = []
            # T-02039 Update the lot values of move and creating the
            # activity for the created lots.
            for (
                everstox_lot
            ) in (
                move.everstox_out_move_return_bind_ids.everstox_stock_move_out_return_lot_ids
            ):
                values = move._prepare_move_line_vals()
                values.update(
                    {
                        "lot_id": everstox_lot.lot_id.id,
                        "qty_done": everstox_lot.product_quantity,
                    }
                )
                move_line_ids.append((0, 0, values))
                if not everstox_lot.move_activity:
                    continue
                self.env["everstox.backend"].create_activity(
                    record=picking,
                    message=(
                        _("The lot %s is not available for the product %s, move %s")
                        % (
                            everstox_lot.lot_id.name,
                            move.product_id.name,
                            move.reference,
                        )
                    ),
                    activity_type="connector_settings.mail_activity_data_error",
                )
            move.move_line_ids = move_line_ids
        # T-02039 creats move line ids
        picking.action_assign()
        picking.with_company(
            picking.sudo().backend_id.company_id
        ).with_delay().button_validate()
        return super()._after_import(binding, **kwargs)


class WooStockPickingOutReturnBatchImporter(Component):

    _name = "woo.stock.picking.out.return.batch.importer"
    _inherit = "woo.delayed.batch.importer"
    _apply_on = "woo.stock.picking.out.return"

    def run(self, filters=None, force=False):
        """#T-02039 Run the synchronization"""
        filters = filters or {}
        if "domain" in filters.keys():
            filters.pop("domain")
        external_ids = self.backend_adapter.search_read(filters)
        count = external_ids.get("count", 0)
        records = external_ids.get("items")
        for record in records:
            self._import_record(record.get("id"), data=record, force=force)
            # T-02244 to call the next batch
        self.process_next_batch(filters, force=force, count=count)

    def _import_record(self, external_id, job_options=None, **kwargs):
        """#T-02039 Delay the import of the records"""
        job_options = job_options or {}
        if "priority" not in job_options:
            job_options["priority"] = 5
        return super(WooStockPickingOutReturnBatchImporter, self)._import_record(
            external_id, job_options, **kwargs
        )
