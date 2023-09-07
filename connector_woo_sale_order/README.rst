**Connector Woo Sale Order**
============================

**Description**
***************

* Technical name: connector_woo_sale_order.
* Create a module named connector_woo_sale_order that extends the functionality of connector_woo_base.
  This module focuses on the import and export of Orders data between Woocommerce and Odoo.
* Add "Import Orders" at backend level.
* Required field to Import the Orders are Location,Client Id,Client Secret.


**Author**
**********

* BizzAppDev


**Used by**
***********

* #N/A


**Installation**
****************

* Under applications, the application connector_woo_sale_order can be installed/uninstalled.


**Configuration**
*****************

* Orders Import:
    - - Navigate to Woocommerce Backends by going to Connectors > Woocommerce > WooCommerce Backends.
    - Add Backend Credentials to Import Orders.
    - Click 'Import Orders' button to Import the Orders from Woocommerce.

**Usage**
*********

* Import of Order Data:
  - Enable the import functionality in connector_woo_sale_order to transfer Orders from Woocommerce to Odoo.
  - Handle mapping of sale order data at time of Import Orders.
  - Enable the form of Sale Order Line and added 'WooCommarce Connector' in sale order line level and added related line calculated field at binding level of sale oder line.
  - Added related sale order amount field at binding level of sale order.
  - Added 'Export Delivery Status' button at sale order level and it will export the Status of sale order to 'Completed' state and carrier_tracking_ref which is located at Stock Picking level in 'Additional info' tab.
  - At backend level,'Mark Order Completed On Delivery' boolean which is located at connectors > WooCommerce > Advanced Configuration tab if 'Mark Order Completed On Delivery' is True then 'Send Tracking Information' will be visible and if 'Mark Order Completed On Delivery' True then State will set 'Completed' in WooCommerce of that Order if 'Mark Order Completed On Delivery' and 'Send Tracking Information' then it will set Order to 'Completed' state and also tracking info will also send in WooCommerce.
  -When the Price Tax, recorded at the Order Line level, differs from the Total Tax Line value, recorded at the Order Line's binding level, a 'Price Tax and Total Tax is Different' Danger Banner will be displayed at the sale order level.


**Known issues/Roadmap**
************************

* #N/A


**Changelog**
*************

* #N/A
