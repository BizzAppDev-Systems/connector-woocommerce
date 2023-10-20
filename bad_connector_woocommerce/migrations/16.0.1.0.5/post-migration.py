import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """
    Added Post Migration Script to add woo_order_status_id and also update the
    woo_order_status_id field.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    cr.execute(
        """
        ALTER TABLE sale_order
        ADD COLUMN IF NOT EXISTS woo_order_status_id INT
        """
    )
    cr.execute(
        """
        ALTER TABLE sale_order
        ADD CONSTRAINT fk_woo_order_status_id
        FOREIGN KEY (woo_order_status_id)
        REFERENCES woo_sale_status(id);
        """
    )
    status_list = [
        "on-hold",
        "completed",
        "pending",
        "processing",
        "cancelled",
        "refunded",
        "failed",
        "trash",
        "auto-draft",
    ]
    for status in status_list:
        status_rec = env["woo.sale.status"].search([("code", "=", status)], limit=1)
        if status_rec:
            cr.execute(
                """
                UPDATE sale_order
                SET woo_order_status_id = %s
                WHERE woo_order_status = %s
                """,
                (status_rec.id, status),
            )
