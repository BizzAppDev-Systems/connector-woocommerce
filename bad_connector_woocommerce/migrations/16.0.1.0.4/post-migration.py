from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    cr.execute(
        """
        ALTER TABLE sale_order
        ADD COLUMN IF NOT EXISTS woo_order_status_id INT;
        """
    )
    status = env["woo.sale.status"].search([("code", "=", "completed")], limit=1)
    if status:
        cr.execute(
            """
            UPDATE sale_order
            SET woo_order_status_id = %d
            WHERE woo_order_status = 'completed'
            """,
            (status.id,),
        )
