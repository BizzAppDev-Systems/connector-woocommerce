import logging

from odoo import api, fields, models

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = "stock.picking"

    woo_bind_ids = fields.One2many(
        comodel_name="woo.stock.picking.refund",
        inverse_name="odoo_id",
        string="WooCommerce Bindings(Stock)",
        copy=False,
    )
    is_refund = fields.Boolean(string="Refund Quantity With Amount")
    sale_woo_binding_ids = fields.One2many(related="sale_id.woo_bind_ids")
    return_picking_id = fields.Many2one("stock.picking", string="Original Picking")
    is_return_stock_picking = fields.Boolean(
        compute="_compute_is_return_stock_picking",
        store=True,
    )

    @api.depends("move_ids_without_package")
    def _compute_is_return_stock_picking(self):
        for picking in self:
            picking.is_return_stock_picking = any(
                m.origin_returned_move_id for m in picking.move_ids_without_package
            )

    def export_refund(self, job_options=None):
        """Export Refund on WooCommerce"""
        woo_model = self.env["woo.stock.picking.refund"]
        if job_options is None:
            job_options = {}
        if "description" not in job_options:
            description = woo_model.export_record.__doc__
        for woo_binding in self.sale_id.woo_bind_ids:
            job_options[
                "description"
            ] = woo_binding.backend_id.get_queue_job_description(
                description, woo_model._description
            )
            woo_model = woo_model.with_delay(**job_options or {})
            woo_model.export_record(woo_binding.backend_id, self)


class WooStockPickingRefund(models.Model):
    _name = "woo.stock.picking.refund"
    _inherit = "woo.binding"
    _inherits = {"stock.picking": "odoo_id"}
    _description = "WooCommerce Stock Picking Refund"

    _rec_name = "name"

    odoo_id = fields.Many2one(
        comodel_name="stock.picking",
        string="Stock Picking",
        required=True,
        ondelete="restrict",
    )


class WooStockPickingRefundAdapter(Component):
    _name = "woo.stock.picking.refund.adapter"
    _inherit = "woo.adapter"
    _apply_on = "woo.stock.picking.refund"

    _woo_model = "orders"
    _woo_key = "id"
    _woo_ext_id_key = "id"

    def create(self, data):
        """Inherited: Inherited this method due to create the resource_path to export
        the refund
        """
        resource_path = "{}/{}/refunds".format(self._woo_model, data["order_id"])
        data.pop("order_id")
        self._woo_model = resource_path
        return super(WooStockPickingRefundAdapter, self).create(data)
