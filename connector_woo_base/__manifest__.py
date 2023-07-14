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
        "data/queue_job_data.xml",
        "security/ir.model.access.csv",
        "views/res_company_views.xml",
        "views/res_config_settings_view.xml",
        "views/woo_backend_view.xml",
        "views/connector_woo_base_menu.xml",
    ],
}
