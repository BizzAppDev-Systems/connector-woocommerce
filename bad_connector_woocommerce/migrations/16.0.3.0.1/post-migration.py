def migrate(cr, version):
    """
    Added Post Migration Script to add woo_order_status_id and also update the
    woo_order_status_id field.
    """
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
        cr.execute(
            """
                UPDATE sale_order
                SET woo_order_status_id =
                (select id from woo_sale_status where code = %s)
                WHERE woo_order_status = %s
            """,
            (status, status),
        )
