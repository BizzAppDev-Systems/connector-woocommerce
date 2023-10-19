import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    cr.execute(
        """
        ALTER TABLE sale_order
        ADD COLUMN IF NOT EXISTS woo_order_status_id INT;
        """
    )
    status = env["woo.sale.status"].search([("code", "=", "completed")], limit=1)
    _logger.info("Status: %s", status)
    if status:
        cr.execute(
            """
            UPDATE sale_order
            SET woo_order_status_id = %s
            WHERE woo_order_status = %s
            """,
            (status.id, "completed"),
        )
