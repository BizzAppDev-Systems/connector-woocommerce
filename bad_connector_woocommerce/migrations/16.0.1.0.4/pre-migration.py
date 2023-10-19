def migrate(cr, version):
    # Check if the column 'woo_order_status' exists in the table
    cr.execute(
        """
        SELECT * FROM information_schema.columns
        WHERE table_name = 'sale_order'
        AND column_name = 'woo_order_status'
        """
    )
    column_exists = cr.fetchone()

    # Add the column 'woo_order_status_id' if it doesn't exist
    if not column_exists:
        cr.execute(
            "ALTER TABLE sale_order ADD COLUMN IF NOT EXISTS woo_order_status_id INT"
        )

    # Update the 'woo_order_status_id' based on 'woo_order_status' values
    cr.execute(
        "UPDATE sale_order SET woo_order_status_id = %s WHERE woo_order_status = %s",
        (4, "completed"),
    )
