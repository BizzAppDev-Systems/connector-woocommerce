import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare

from odoo.addons.component.core import Component
from odoo.addons.connector_woo_base.components.binder import WooModelBinder

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    woo_bind_ids = fields.One2many(
        comodel_name="woo.sale.order",
        inverse_name="odoo_id",
        string="WooCommerce Bindings",
        copy=False,
    )
    has_done_picking = fields.Boolean(
        string="Has Done Picking", compute="_compute_has_done_picking", store=True
    )
    # TODO: phase 2 convert me to compute.
    woo_order_status = fields.Selection(
        selection=[
            ("completed", "Completed"),
            ("any", "Any"),
            ("pending", "Pending"),
            ("processing", "Processing"),
            ("on-hold", "Hold"),
            ("cancelled", "Cancelled"),
            ("refunded", "Refunded"),
            ("failed", "Failed"),
            ("trash", "Trash"),
        ],
        string="WooCommerce Order Status",
        default="any",
    )
    tax_different = fields.Boolean(compute="_compute_tax_diffrent")
    total_amount_different = fields.Boolean(compute="_compute_total_amount_diffrent")

    @api.depends(
        "woo_bind_ids",
        "order_line.woo_bind_ids.total_tax_line",
        "order_line.price_tax",
    )
    def _compute_tax_diffrent(self):
        """
        Compute the 'tax_different' field for the sale order.

        This method calculates whether the tax amounts on WooCommerce order lines
        are different from the total tax amount of the order binding. If there is any
        inconsistency, it sets the 'tax_different' field to True; otherwise, it remains
        False.
        """
        for order in self:
            tax_different = False
            if any(
                [
                    float_compare(
                        line.price_tax,
                        line.total_tax_line,
                        precision_rounding=order.currency_id.rounding,
                    )
                    != 0
                    for line in order.mapped("woo_bind_ids").mapped(
                        "woo_order_line_ids"
                    )
                ]
            ):
                tax_different = True
            order.tax_different = tax_different

    @api.depends("amount_total", "woo_bind_ids.woo_amount_total")
    def _compute_total_amount_diffrent(self):
        """
        Compute the 'total_amount_different' field for each record in the current recordset.

        This method is used to calculate whether there is a difference in the total amount between the
        current sales order and its related WooCommerce bindings. The 'total_amount_different' field
        indicates whether the total amounts differ among the bindings.
        """
        for order in self:
            amount_total_different = False
            if any(
                [
                    float_compare(
                        order.amount_total,
                        binding.woo_amount_total,
                        precision_rounding=order.currency_id.rounding,
                    )
                    != 0
                    for binding in order.mapped("woo_bind_ids")
                ]
            ):
                amount_total_different = True
            order.total_amount_different = amount_total_different

    @api.depends("picking_ids", "picking_ids.state")
    def _compute_has_done_picking(self):
        """Check all Picking is in done state"""
        for order in self:
            if not order.picking_ids:
                order.has_done_picking = False
            else:
                order.has_done_picking = all(
                    picking.state == "done" for picking in order.picking_ids
                )

    def validate_delivery_orders_done(self):
        """
        Add validations on creation and process of fulfillment orders
        based on delivery order state.
        """
        picking_ids = self.picking_ids.filtered(lambda p: p.state == "done")
        if not picking_ids:
            raise ValidationError(_("No delivery orders in 'done' state."))
        if self.woo_order_status == "completed":
            raise ValidationError(
                _("WooCommerce Sale Order is already in Completed Status.")
            )

    def export_delivery_status(self):
        """Change state of a sales order on WooCommerce"""
        for binding in self.woo_bind_ids:
            self.validate_delivery_orders_done()
            binding.update_woo_order_fulfillment_status()


class WooSaleOrder(models.Model):
    _name = "woo.sale.order"
    _inherit = "woo.binding"
    _inherits = {"sale.order": "odoo_id"}
    _description = "WooCommerce Sale Order"

    _rec_name = "name"

    odoo_id = fields.Many2one(
        comodel_name="sale.order",
        string="Sale Order",
        required=True,
        ondelete="restrict",
    )
    woo_order_line_ids = fields.One2many(
        comodel_name="woo.sale.order.line",
        inverse_name="woo_order_id",
        string="WooCommerce Order Lines",
        copy=False,
    )
    woo_order_id = fields.Integer(
        string="WooCommerce Order ID", help="'order_id' field in WooCommerce"
    )
    discount_total = fields.Monetary()
    discount_tax = fields.Monetary()
    shipping_total = fields.Monetary()
    shipping_tax = fields.Monetary()
    cart_tax = fields.Monetary()
    total_tax = fields.Monetary()
    price_unit = fields.Monetary()
    woo_amount_total = fields.Monetary()

    def __init__(self, name, bases, attrs):
        """Bind Odoo Partner"""
        WooModelBinder._apply_on.append(self._name)
        super(WooSaleOrder, self).__init__(name, bases, attrs)

    def update_woo_order_fulfillment_status(self):
        """Change status of a sales order on WooCommerce"""
        self.ensure_one()
        with self.backend_id.work_on(self._name) as work:
            exporter = work.component(usage="record.exporter")
            return exporter.run(self)


class WooSaleOrderAdapter(Component):
    _name = "woo.sale.order.adapter"
    _inherit = "woo.adapter"
    _apply_on = "woo.sale.order"

    _woo_model = "orders"
    _woo_key = "id"
    _woo_ext_id_key = "id"
    _model_dependencies = [
        (
            "woo.res.partner",
            "customer_id",
        ),
    ]


# Sale order line


class WooSaleOrderLine(models.Model):
    _name = "woo.sale.order.line"
    _inherit = "woo.binding"
    _description = "WooCommerce Sale Order Line"
    _inherits = {"sale.order.line": "odoo_id"}

    woo_order_id = fields.Many2one(
        comodel_name="woo.sale.order",
        string="WooCommerce Order Line",
        required=True,
        ondelete="cascade",
        index=True,
    )
    odoo_id = fields.Many2one(
        comodel_name="sale.order.line",
        string="Sale Order Line",
        required=True,
        ondelete="restrict",
    )
    total_tax_line = fields.Monetary()
    price_subtotal_line = fields.Monetary(string="Total Line")
    subtotal_tax_line = fields.Monetary()
    subtotal_line = fields.Monetary()

    def __init__(self, name, bases, attrs):
        """Bind Odoo Sale Order Line"""
        WooModelBinder._apply_on.append(self._name)
        super(WooSaleOrderLine, self).__init__(name, bases, attrs)

    @api.model_create_multi
    def create(self, vals):
        for value in vals:
            existing_record = self.search(
                [
                    ("external_id", "=", value.get("external_id")),
                    ("backend_id", "=", value.get("backend_id")),
                ]
            )
            if not existing_record:
                binding = self.env["woo.sale.order"].browse(value["woo_order_id"])
                value["order_id"] = binding.odoo_id.id
        return super(WooSaleOrderLine, self).create(vals)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    woo_bind_ids = fields.One2many(
        comodel_name="woo.sale.order.line",
        inverse_name="odoo_id",
        string="WooCommerce Bindings(Order Line)",
        copy=False,
    )
    woo_line_id = fields.Char()
