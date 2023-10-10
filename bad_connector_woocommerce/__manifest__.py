{
    "name": "Odoo Woocommerce Connector",
    "version": "16.0.1.0.4",
    "category": "Connector",
    "author": "BizzAppDev Systems Pvt. Ltd.",
    "website": "http://www.bizzappdev.com",
    "depends": [
        "connector",
        "mail",
        "contacts",
        "product",
        "sale_management",
        "delivery",
    ],
    "license": "LGPL-3",
    "data": [
        "data/queue_job_data.xml",
        "data/ir_cron_data.xml",
        "data/woo_status_data.xml",
        "security/ir.model.access.csv",
        "views/res_company_views.xml",
        "views/res_config_settings_view.xml",
        "views/woo_backend_view.xml",
        "views/product_attribute_value_view.xml",
        "views/product_attribute_view.xml",
        "views/product_views.xml",
        "views/product_category_view.xml",
        "views/res_partner_views.xml",
        "views/sale_order_view.xml",
        "views/woo_sale_status_view.xml",
        "views/connector_woo_base_menu.xml",
    ],
    "images": ["static/description/banner.gif"],
    "external_dependencies": {
        "python": ["woocommerce"],
    },
    "price": 50,
    "currency": "EUR",
}
