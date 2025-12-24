{
    "name": "Stock Route Carrier Propagation",
    "summary": "Propagate delivery carrier from route to stock operations",
    "description": "\n    This module extends Odoo's routing functionality to allow a Delivery Carrier\n    (Shipping Method) to be configured at the Route level and automatically\n    propagated to the related Stock Operations (Pickings) created from that route.\n    ",
    "version": "16.0.1.0.0",
    "category": "Inventory",
    "author": "Your Company",
    "license": "AGPL-3",
    "depends": [
        "delivery",
    ],
    "data": [
        "views/stock_route_views.xml",
    ],
    "installable": True,
    "auto_install": False,
}
