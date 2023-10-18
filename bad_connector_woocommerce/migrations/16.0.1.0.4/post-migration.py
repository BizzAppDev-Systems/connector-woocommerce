def migrate(cr, version):
    cr.execute(
        """
        ALTER TABLE sale_order
        DROP COLUMN IF EXISTS woo_order_status;
        """
    )
    cr.execute(
        """
        ALTER TABLE sale_order
        ADD COLUMN IF NOT EXISTS woo_order_status_id INT;
        """
    )
