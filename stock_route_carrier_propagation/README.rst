Stock Route Carrier Propagation Module
=====================================

This module extends Odoo's routing functionality to allow a Delivery Carrier
(Shipping Method) to be configured at the Route level and automatically
propagated to the related Stock Operations (Pickings) created from that route.

Features
--------

* Adds a 'Default Delivery Carrier' field to stock routes
* Automatically sets carrier on pickings based on route configuration
* Demo data included for testing

Installation
------------

1. Install the module through Odoo's interface or via command line
2. Go to Inventory > Configuration > Routes
3. Create or edit a route and set the carrier in the 'Default Delivery Carrier' field

Usage
-----

1. Configure a route with a delivery carrier
2. When a picking is created from that route, the carrier will be automatically set

Technical Details
---------------

* Extends ``stock.route`` model with ``carrier_id`` field
* Extends ``stock.picking`` model with ``_prepare_procurement_values`` method
* Uses Odoo's procurement system for automatic carrier propagation

Author
------

Your Company

License
-------

AGPL-3
