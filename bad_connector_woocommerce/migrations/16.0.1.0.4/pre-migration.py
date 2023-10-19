def migrate(cr, version):
    cr.execute(
        """
        ALTER TABLE sale_order
        ADD COLUMN IF NOT EXISTS woo_order_status_id INT
        """
    )
    cr.execute(
        """
        UPDATE sale_order
        SET woo_order_status_id = 4
        WHERE woo_order_status = 'completed'
        """
    )
