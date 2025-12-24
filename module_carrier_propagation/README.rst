Delivery Carrier Propagation from Route to Stock Operations
===========================================================

This module enables carrier propagation from route definitions to stock operations.

Features
--------

* Adds carrier_id field to route form view
* Propagates carrier information from routes to stock pickings
* Integrates with Odoo's stock and delivery modules

Installation
------------

This module requires the following dependencies:

* stock
* delivery

Usage
-----

1. Go to Inventory > Configuration > Routes
2. Select a route and assign a carrier in the carrier_id field
3. When stock operations are created from this route, the carrier will be automatically propagated to the picking

Technical Details
-----------------

The module extends stock.move._get_new_picking_values() to automatically set the carrier_id on pickings
created from routes that have carriers assigned.
