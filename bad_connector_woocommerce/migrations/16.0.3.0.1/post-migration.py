def migrate(cr, version):
    cr.execute(
        """
        UPDATE your_table_name
        SET warehouse_id =  (select id from stock_warehouse where code = "WH")
        WHERE warehouse_id IS NULL;
        """
    )
