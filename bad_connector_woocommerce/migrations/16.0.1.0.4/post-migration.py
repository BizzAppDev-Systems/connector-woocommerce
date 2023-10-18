def migrate(cr, version):
    cr.execute(
        """
        ALTER TABLE sale_order
        ADD COLUMN IF NOT EXISTS woo_order_status_id INT;
        """
    )
    cr.execute(
        """
        UPDATE sale_order
        SET woo_order_status_id =
            CASE
                WHEN woo_order_status = 'pending' THEN 1
                WHEN woo_order_status = 'processing' THEN 2
                WHEN woo_order_status = 'on-hold' THEN 3
                WHEN woo_order_status = 'completed' THEN 4
                WHEN woo_order_status = 'cancelled' THEN 5
                WHEN woo_order_status = 'refunded' THEN 6
                WHEN woo_order_status = 'failed' THEN 7
                WHEN woo_order_status = 'trash' THEN 8
                WHEN woo_order_status = 'auto-draft' THEN 9
                ELSE 0
            END;
        """
    )
    cr.execute(
        """
        ALTER TABLE sale_order
        DROP COLUMN IF EXISTS woo_order_status;
        """
    )
