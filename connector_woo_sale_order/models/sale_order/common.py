import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

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
        string="Has Done Picking", compute="_compute_has_done_picking"
    )
    woo_order_status = fields.Selection(
        selection=[
            ("completed", "Completed"),
            ("null", "Null"),
        ],
        string="WooCommerce Order Status",
    )
    tax_different = fields.Boolean(compute="_compute_tax_diffrent")

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
                    line.price_tax != line.total_tax_line
                    for line in order.mapped("woo_bind_ids").mapped(
                        "woo_order_line_ids"
                    )
                ]
            ):
                tax_different = True
            order.tax_different = tax_different

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

    def check_export_fulfillment(self):
        """
        Add validations on creation and process of fulfillment orders
        based on delivery order state.
        """
        picking_ids = self.picking_ids.filtered(lambda p: p.state == "done")
        if not picking_ids:
            raise ValidationError(_("No delivery orders in 'done' state."))

    def export_delivery_status(self, allowed_states=None, comment=None, notify=None):
        """Change state of a sales order on WooCommerce"""
        for binding in self.woo_bind_ids:
            if self._context.get("state"):
                binding.with_delay(
                    priority=5,
                ).export_fulfillment()
            else:
                self.check_export_fulfillment()
                binding.export_fulfillment()


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
    discount_total = fields.Float()
    discount_tax = fields.Float()
    shipping_total = fields.Float()
    shipping_tax = fields.Float()
    cart_tax = fields.Float()
    total_tax = fields.Float()
    price_unit = fields.Float()
    price_subtotal = fields.Float()
    woo_amount_total = fields.Float()

    def __init__(self, name, bases, attrs):
        """Bind Odoo Partner"""
        WooModelBinder._apply_on.append(self._name)
        super(WooSaleOrder, self).__init__(name, bases, attrs)

    def export_fulfillment(self):
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
    total_tax_line = fields.Float()
    price_subtotal_line = fields.Float()
    subtotal_tax_line = fields.Float()
    subtotal_line = fields.Float()

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
