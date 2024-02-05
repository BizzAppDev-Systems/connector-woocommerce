from odoo import fields, models

from odoo.addons.component.core import Component


class StockPicking(models.Model):
    _inherit = "stock.picking"

    woo_out_return_bind_ids = fields.One2many(
        comodel_name="woo.stock.picking.out.return",
        inverse_name="odoo_id",
        string="WooCommerce Bindings",
        copy=False,
    )
    # everstox_return_id = fields.Char(
    #     string="Everstox Return ID",
    #     related="everstox_out_return_bind_ids.external_id",
    #     readonly=True,
    # )
    # everstox_out_return_status_id = fields.Many2one(
    #     string="Everstox Return Status",
    #     related="everstox_out_return_bind_ids.everstox_return_status_id",
    #     readonly=True,
    #     ondelete="restrict",
    # )
    # everstox_return_last_update_date = fields.Datetime(
    #     string="Last Updated Date Of Return",
    # )

    # def get_incoming_picking_return(self):
    #     """#T-02039 Find picking for incoming (of sale)"""
    #     return self.filtered(
    #         lambda picking: picking.picking_type_code == "incoming" and picking.sale_id
    #     )

    # def get_return_binding(self):
    #     """# T-02039 Return the picking which has external_id"""
    #     picking_return = self.get_incoming_picking_return()
    #     if picking_return:
    #         return self.everstox_out_return_bind_ids.filtered(
    #             lambda binding: binding.external_id
    #         )
    #     return picking_return

    # @api.depends(
    #     "everstox_out_return_bind_ids.everstox_return_updated_date",
    #     "everstox_out_return_bind_ids",
    # )
    # def _compute_last_update_date(self):
    #     """#T-02039 computes the last updated date of return"""
    #     picking_return = self.get_incoming_picking_return()
    #     for picking in picking_return:
    #         binding = picking.get_return_binding()
    #         # T-02320 Fixing:- issue regarding not getting the last_update_date
    #         picking.last_update_date = (
    #             binding and binding[:1].everstox_return_updated_date
    #         )
    #         picking.everstox_return_last_update_date = (
    #             binding and binding[:1].everstox_return_updated_date
    #         )
    #     super(StockPicking, (self - picking_return))._compute_last_update_date()

    # @api.depends(
    #     "everstox_out_return_bind_ids",
    #     "everstox_out_return_status_id",
    # )
    # def _compute_remote_status(self):
    #     """# T-02039 compute current everstox status"""
    #     picking_return = self.get_incoming_picking_return()
    #     for picking in picking_return:
    #         picking.status_id = picking.everstox_out_return_status_id
    #         picking.status = picking.status_id.name
    #     super(StockPicking, (self - picking_return))._compute_remote_status()

    # def update_status_new_return(self):
    #     pass

    # def update_status_waiting_for_decision_return(self):
    #     pass

    # def update_status_resolved_return(self):
    #     pass

    # def update_status_needs_attention_return(self):
    #     pass

    # def _action_done(self):
    #     """#T-02243 export the return status if return of main company goes to done."""
    #     bindings = self.filtered(
    #         lambda p: p.company_id.company_type == "main_company"
    #         and p.everstox_out_return_bind_ids
    #     ).mapped("everstox_out_return_bind_ids")
    #     if not bindings:
    #         return super(StockPicking, self)._action_done()
    #     move_binding = self.env["everstox.stock.move.out.return"]
    #     for move in bindings.everstox_stock_move_out_ids:
    #         move_binding.with_company(
    #             move.sudo().backend_id.company_id
    #         ).with_delay().export_record(move.backend_id, move.odoo_id)
    #     return super(StockPicking, self)._action_done()


class WooStockPickingOutReturn(models.Model):
    _name = "woo.stock.picking.out.return"
    _inherit = ["woo.binding"]
    _inherits = {"stock.picking": "odoo_id"}
    _description = "WooCommerce Stock Picking"

    _sql_constraints = [
        (
            "unique_backend_id_odoo_id",
            "unique (backend_id, odoo_id)",
            "Backend ID with Odoo ID must be unique for WooCommerce Records",
        )
    ]

    odoo_id = fields.Many2one(
        comodel_name="stock.picking",
        string="Odoo Returns",
        ondelete="restrict",
        required=True,
    )
    # everstox_return_status_id = fields.Many2one(
    #     comodel_name="remote.shipment.status",
    #     string="Everstox Status",
    #     readonly=True,
    #     copy=False,
    # )

    # everstox_return_date = fields.Datetime(string="Return Created")
    # everstox_return_updated_date = fields.Datetime(string="Return Updated")
    # everstox_stock_move_out_ids = fields.One2many(
    #     comodel_name="everstox.stock.move.out.return",
    #     inverse_name="everstox_return_id",
    #     string="Everstox Stock Move",
    #     copy=False,
    # )

    # def action_open_in_everstox_return(self):
    #     """#T-02353 Action for open everstox for Return in new tab"""
    #     client_action = self.backend_id.get_url_everstox(binding=self)
    #     return client_action


class WooStockPickingOutReturnAdapter(Component):
    _inherit = "woo.adapter"
    _name = "woo.stock.picking.out.return.adapter"
    _woo_model = "orders"
    _remote_ext_id_key = "id"

    def search(self, filters=None, **kwargs):
        """
        Overrides:This method overrides
        """
        resource_path = "{}/{}/refunds".format(self._woo_model, filters.get("order_id"))
        result = self._call(
            resource_path=resource_path, arguments=filters, http_method="get"
        )
        for res in result.get("data"):
            res["attribute"] = filters.get("attribute")
        return result
