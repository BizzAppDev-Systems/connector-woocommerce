{
    "name": "Connector Woo Base",
    "version": "16.0.1.0.0",
    "category": "Connector",
    "author": "BizzAppDev",
    "website": "http://www.bizzappdev.com",
    "depends": ["connector", "mail"],
    "external_dependencies": {"python": ["requests", "simplejson"]},
    "license": "LGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "data/queue_job_data.xml",
        "views/woo_backend_view.xml",
        "views/res_partner_views.xml",
        "views/connector_woo_base_menu.xml",
    ],
}
