import logging

from odoo import api, fields, models
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
    woo_backend_id = fields.Many2one(
        comodel_name="woo.backend",
        string="WooCommerce Backend",
        ondelete="restrict",
    )
    discount_total = fields.Float(string="Discount Total")
    discount_tax = fields.Float(string="Discount Tax")
    shipping_total = fields.Float(string="Shipping Total")
    shipping_tax = fields.Float(string="Shipping Tax")
    cart_tax = fields.Float(string="Cart Tax")
    total_tax = fields.Float(string="Total Tax")
    price_unit = fields.Float(string="Price Total")
    price_subtotal = fields.Float(string="Price Subtotal")
    amount_total = fields.Float(string="Amount Total")

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
            raise ValidationError("No delivery orders in 'done' state.")

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

    def __init__(self, name, bases, attrs):
        """Bind Odoo Partner"""
        WooModelBinder._apply_on.append(self._name)
        super(WooSaleOrder, self).__init__(name, bases, attrs)

    def export_fulfillment(self):
        """Change status of a sales order on shopify"""
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
    _odoo_ext_id_key = "id"


# Sale order line


class WooSaleOrderLine(models.Model):
    _name = "woo.sale.order.line"
    _inherit = "woo.binding"
    _description = "WooCommerce Sale Order Line"
    _inherits = {"sale.order.line": "odoo_id"}

    woo_order_id = fields.Many2one(
        comodel_name="woo.sale.order",
        string="WooCommerce Sale Order",
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
    backend_id = fields.Many2one(
        related="woo_order_id.backend_id",
        string="WooCommerce Backend(Woo Line)",
        readonly=True,
        store=True,
        required=False,
    )

    def __init__(self, name, bases, attrs):
        """Bind Odoo Sale Order Line"""
        WooModelBinder._apply_on.append(self._name)
        super(WooSaleOrderLine, self).__init__(name, bases, attrs)

    @api.model
    def create(self, vals):
        existing_record = self.search(
            [
                ("external_id", "=", vals.get("external_id")),
                ("backend_id", "=", vals.get("backend_id")),
            ]
        )
        if existing_record:
            _logger.warning("Duplicate record creation detected: %s", vals)
            return existing_record
        else:
            binding = self.env["woo.sale.order"].browse(vals["woo_order_id"])
            vals["order_id"] = binding.odoo_id.id
            binding = super(WooSaleOrderLine, self).create(vals)
            return binding


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    woo_bind_ids = fields.One2many(
        comodel_name="woo.sale.order.line",
        inverse_name="odoo_id",
        string="Woo Bindings",
        copy=False,
    )
    woo_line_id = fields.Char()
    woo_backend_id = fields.Many2one(
        comodel_name="woo.backend",
        string="WooCommerce Backend(Line)",
        ondelete="restrict",
    )
