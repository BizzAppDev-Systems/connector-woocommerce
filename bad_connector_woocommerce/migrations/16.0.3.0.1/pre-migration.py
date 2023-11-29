def migrate(cr, version):
    """
    Added Pre Migration Script to add woo_order_status_id and also update the
    woo_order_status_id field.
    """
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
