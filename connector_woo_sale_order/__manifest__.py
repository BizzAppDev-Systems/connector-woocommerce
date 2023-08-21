{
    "name": "Connector Woo Sale Order",
    "version": "16.0.1.0.0",
    "category": "Connector",
    "author": "BizzAppDev",
    "website": "http://www.bizzappdev.com",
    "depends": [
        "sale_management",
        "connector_woo_product",
        "connector_woo_partner",
        "connector_ecommerce",
    ],
    "license": "LGPL-3",
    "data": [
        "data/queue_job_data.xml",
        "data/ir_cron_data.xml",
        "security/ir.model.access.csv",
        "views/woo_backend_view.xml",
        "views/sale_order_view.xml",
        # "views/stock_picking_view.xml"
    ],
}
