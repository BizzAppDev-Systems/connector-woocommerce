import logging

from odoo import fields, models

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    woo_bind_ids = fields.One2many(
        comodel_name="woo.product.product",
        inverse_name="odoo_id",
        string="Woo Bindings",
        copy=False,
    )
    woo_backend_id = fields.Many2one(
        comodel_name="woo.backend",
        string="Woo Backend",
        ondelete="restrict",
    )


class WooSaleOrder(models.Model):
    _name = "woo.sale.order"
    _inherit = "woo.binding"
    _inherits = {"sale.order": "odoo_id"}
    _description = "Woo Sale Order"

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
        string="Woo Order Lines",
        copy=False,
    )


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
    _description = "Woo Sale Order Line"
    _inherits = {"sale.order.line": "odoo_id"}

    woo_order_id = fields.Many2one(
        comodel_name="woo.sale.order",
        string="Woo Sale Order",
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
        string="Woo Backend",
        readonly=True,
        store=True,
        required=False,
    )


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    woo_bind_ids = fields.One2many(
        comodel_name="woo.sale.order.line",
        inverse_name="odoo_id",
        string="Woo Bindings",
        copy=False,
    )
    woo_line_id = fields.Char()
