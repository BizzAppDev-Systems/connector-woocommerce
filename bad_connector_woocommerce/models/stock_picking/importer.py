import logging

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class WooStockPickingRefundImporter(Component):
    _name = "woo.stock.picking.refund.importer"
    _inherit = "woo.delayed.batch.importer"
    _apply_on = "woo.stock.picking.refund"


class WooStockPickingRefundExporterMapper(Component):
    _name = "woo.stock.picking.refund.import.mapper"
    _inherit = "woo.import.mapper"
    _apply_on = "woo.stock.picking.refund"


class WooStockPickingRefundBatchImporter(Component):
    _name = "woo.stock.picking.refund.batch.exporter"
    _inherit = "woo.importer"
    _apply_on = ["woo.stock.picking.refund"]
    _default_binding_field = "woo_return_bind_ids"

    def _get_remote_data(self, **kwargs):
        """Return the raw data for ``self.external_id``"""
        attributes = {}
        data = self.backend_adapter.read(self.external_id, attributes=attributes)
        if not data.get(self.backend_adapter._woo_ext_id_key):
            data[self.backend_adapter._woo_ext_id_key] = self.external_id
        print(
            data,
            "ppppppppp its a data from _get_remote_data_get_remote_data_get_remote_data",
        )
        return data

    def _create(self, data):
        """Create the OpenERP record"""
        # special check on data before import
        res = super(WooStockPickingRefundBatchImporter, self)._create(data)
        binder = self.binder_for(model="woo.sale.order")
        sale_order = binder.to_internal(self.remote_record.get("order_id"), unwrap=True)
        delivery_order = sale_order.picking_ids[0]
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
        for line in self.remote_record.get("line_items"):
            quantity = abs(line.get("quantity"))
            product_id = binder.to_internal(line.get("product_id"), unwrap=True).id
            if product_id not in product_grouped_qty:
                product_grouped_qty[product_id] = 0
            product_grouped_qty[product_id] += quantity
            if product_id not in product_return_qty:
                product_return_qty[product_id] = []
            product_return_qty[product_id].append([line.get("id"), quantity])
        print(product_grouped_qty, product_return_qty, "plllllllllllppppppppppppppp")
        for item in self.remote_record.get("line_items"):
            product_id = binder.to_internal(item.get("product_id"), unwrap=True).id
            return_line = return_wizard.product_return_moves.filtered(
                lambda r: r.product_id.id == product_id
            )
            # T-02039 move_external_id does have a value of external_id of moves and
            # update quantity set the external id for move.
            return_line.update(
                {
                    "quantity": float(product_grouped_qty[product_id]),
                }
            )
        picking_returns = return_wizard._convert_to_write(
            {name: return_wizard[name] for name in return_wizard._cache}
        )
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
        print()
        # T-02039 creates return for the picking with the moves.
        stock_return_picking = (
            self.env["stock.return.picking"]
            .with_context(do_not_merge=True)
            .create(picking_returns)
        )
        print(stock_return_picking, "pppppppppsssssssssssssmmmmmmmmmmmmmm")
        return_id, return_type = stock_return_picking._create_returns()
        data["odoo_id"] = return_id
        picking_id = self.env["stock.picking"].browse(return_id)
        print(picking_id, "lplplplplplplpl")
        return res
