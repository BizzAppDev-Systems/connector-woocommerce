import logging

from odoo import _, api, fields, models

from odoo.addons.component.core import Component

# from odoo.exceptions import ValidationError
# from odoo.tools import float_compare


_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = "stock.picking"

    woo_bind_ids = fields.One2many(
        comodel_name="woo.stock.picking.refund",
        inverse_name="odoo_id",
        string="WooCommerce Bindings",
        copy=False,
    )
    is_refund = fields.Boolean(string="Refund")

    def export_refund(self):
        """Change state of a sales order on WooCommerce"""
        print(self, ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;")
        for binding in self.woo_bind_ids:
        #     if not binding.backend_id.mark_completed:
        #         raise ValidationError(
        #             _(
        #                 "Export Delivery Status is Not Allow from WooCommerce"
        #                 " Backend '%s'.",
        #                 binding.backend_id.name,
        #             )
        #         )
        #     binding.update_woo_order_fulfillment_status()


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

    # def update_woo_order_fulfillment_status(self, job_options=None):
    #     """Change status of a sales order on WooCommerce"""
    #     woo_model = self.env["woo.stock.picking.refund"]
    #     if self._context.get("execute_from_cron"):
    #         if job_options is None:
    #             job_options = {}
    #         if "description" not in job_options:
    #             description = self.export_record.__doc__
    #             job_options["description"] = self.backend_id.get_queue_job_description(
    #                 description, self._description
    #             )
    #         woo_model = woo_model.with_delay(**job_options or {})
    #     for woo_order in self:
    #         # if not self._context.get("execute_from_cron"):
    #         #     woo_order.validate_delivery_orders_done()
    #         woo_model.export_record(woo_order.backend_id, woo_order)

    # def validate_delivery_orders_done(self):
    #     """
    #     Add validations on creation and process of fulfillment orders
    #     based on delivery order state.
    #     """
    #     picking_ids = self.mapped("picking_ids").filtered(
    #         lambda p: p.state in ["done", "cancel"]
    #     )
    #     if not picking_ids:
    #         raise ValidationError(_("No delivery orders in 'done' state."))
    #     if self.is_final_status:
    #         raise ValidationError(
    #             _("WooCommerce Sale Order is already in Completed Status.")
    #         )
    #     for woo_order in self:
    #         no_tracking_do = picking_ids.filtered(lambda p: not p.carrier_tracking_ref)
    #         if woo_order.backend_id.tracking_info and no_tracking_do:
    #             do_names = ", ".join(no_tracking_do.mapped("name"))
    #             raise ValidationError(
    #                 _("Tracking Reference not found in Delivery Order! %s" % do_names)
    #             )

    # def update_woo_order_fulfillment_status(self, job_options=None):
    #     """Change status of a sales order on WooCommerce"""
    #     woo_model = self.env["woo.sale.order"]
    #     if self._context.get("execute_from_cron"):
    #         if job_options is None:
    #             job_options = {}
    #         if "description" not in job_options:
    #             description = self.export_record.__doc__
    #             job_options["description"] = self.backend_id.get_queue_job_description(
    #                 description, self._description
    #             )
    #         woo_model = woo_model.with_delay(**job_options or {})
    #     for woo_order in self:
    #         if not self._context.get("execute_from_cron"):
    #             woo_order.validate_delivery_orders_done()
    #         woo_model.export_record(woo_order.backend_id, woo_order)


class WooStockPickingReturnAdapter(Component):
    _name = "woo.stock.picking.return.adapter"
    _inherit = "woo.adapter"
    _apply_on = "woo.stock.picking.return"

    _woo_model = "refunds"
    _woo_key = "id"
    _woo_ext_id_key = "id"
    # _model_dependencies = [
    #     (
    #         "woo.res.partner",
    #         "customer_id",
    #     ),
    # ]


# # Sale order line


# class WooSaleOrderLine(models.Model):
#     _name = "woo.sale.order.line"
#     _inherit = "woo.binding"
#     _description = "WooCommerce Sale Order Line"
#     _inherits = {"sale.order.line": "odoo_id"}

#     woo_order_id = fields.Many2one(
#         comodel_name="woo.sale.order",
#         string="WooCommerce Order Line",
#         required=True,
#         ondelete="cascade",
#         index=True,
#     )
#     odoo_id = fields.Many2one(
#         comodel_name="sale.order.line",
#         string="Sale Order Line",
#         required=True,
#         ondelete="restrict",
#     )
#     total_tax_line = fields.Monetary()
#     price_subtotal_line = fields.Monetary(string="Total Line")
#     subtotal_tax_line = fields.Monetary()
#     subtotal_line = fields.Monetary()

#     @api.model_create_multi
#     def create(self, vals):
#         """
#         Create multiple WooSaleOrderLine records.

#         :param vals: List of dictionaries containing values for record creation.
#         :type vals: list of dict
#         :return: Created WooSaleOrderLine records.
#         :rtype: woo.sale.order.line
#         """
#         for value in vals:
#             existing_record = self.search(
#                 [
#                     ("external_id", "=", value.get("external_id")),
#                     ("backend_id", "=", value.get("backend_id")),
#                 ]
#             )
#             if not existing_record:
#                 binding = self.env["woo.sale.order"].browse(value["woo_order_id"])
#                 value["order_id"] = binding.odoo_id.id
#         return super(WooSaleOrderLine, self).create(vals)


# class SaleOrderLine(models.Model):
#     _inherit = "sale.order.line"

#     woo_bind_ids = fields.One2many(
#         comodel_name="woo.sale.order.line",
#         inverse_name="odoo_id",
#         string="WooCommerce Bindings(Order Line)",
#         copy=False,
#     )
#     woo_line_id = fields.Char()
