def migrate(cr, version):
    warehouse = "WH"
    cr.execute(
        """
        UPDATE woo_backend
        SET warehouse_id =
        (SELECT id FROM stock_warehouse WHERE code = %s)
        WHERE warehouse_id IS NULL;
        """,
        (warehouse,),
    )
