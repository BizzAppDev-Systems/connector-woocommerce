{
    "name": "Odoo Woocommerce Connector",
    "version": "17.0.1.0.0",
    "category": "Connector",
    "author": "BizzAppDev Systems Pvt. Ltd.",
    "website": "http://www.bizzappdev.com",
    "depends": [
        "connector",
        "mail",
        "contacts",
        "sale_management",
        "delivery",
        "sale_automatic_workflow",
        "stock_return_reason",
    ],
    "license": "AGPL-3",
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
        "views/product_tag_view.xml",
        "views/woo_tax_view.xml",
        "views/product_views.xml",
        "views/res_country_view.xml",
        "views/product_category_view.xml",
        "views/woo_product_image_url_view.xml",
        "views/res_partner_views.xml",
        "views/sale_order_view.xml",
        "views/woo_sale_status_view.xml",
        "views/delivery_carrier_view.xml",
        "views/woo_settings_view.xml",
        "views/woo_payment_gateway_views.xml",
        "views/queue_job_view.xml",
        "views/product_template_view.xml",
        "views/woo_downloadable_product_views.xml",
        "views/stock_picking.xml",
        "views/connector_woo_base_menu.xml",
    ],
    "images": ["static/description/banner.gif"],
    "external_dependencies": {
        "python": ["woocommerce"],
    },
}
