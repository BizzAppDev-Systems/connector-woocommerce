from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    sale_orders = env["sale.order"].search([])

    for order in sale_orders:
        woo_order_status_id = env["woo.sale.status"].search(
            [("code", "=", order.woo_order_status)], limit=1
        )
        if woo_order_status_id:
            order.write({"woo_order_status_id": woo_order_status_id.id})
