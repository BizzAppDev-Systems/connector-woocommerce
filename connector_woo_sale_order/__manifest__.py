{
    "name": "Connector Woo Sale Order",
    "version": "16.0.1.0.0",
    "category": "Connector",
    "author": "BizzAppDev",
    "website": "http://www.bizzappdev.com",
    "depends": ["connector_woo_products", "connector_woo_partners"],
    "external_dependencies": {"python": ["requests", "simplejson"]},
    "license": "LGPL-3",
    "data": [
        "data/queue_job_data.xml",
        "data/ir_cron_data.xml",
        "security/ir.model.access.csv",
        "views/woo_backend_view.xml",
        "views/product_views.xml",
    ],
}
