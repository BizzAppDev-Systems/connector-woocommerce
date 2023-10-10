**Odoo Woocommerce Connector**
==============================

**Description**
***************

* Technical name: bad_connector_woocommerce.
* Add new menu in Connectors > Woocommerce > WooCommerce Backends.
* Add new menu in Connectors > Configrations > Settings.
* Add object woo.backend and woo.product.category on submenu Connectors.
* Required field are Location,Client Key,Client Secret.
* 'Test' mode is used to test the environment using test data, while the 'Production' mode is used for the live environment that contains real customer data and requires production-level credentials.
* Create a module named bad_connector_woocommerce This module focuses on the import of "Customers", "Products","Product Attributes","Product Categories", "Orders" and export of "Orders" data between connected Woocommerce and Odoo.
* Add "Import Partners","Import Products","Import Product Attributes","Import Product Category" and "Import Orders" at backend level.
* Required field to Import the Products,Product Attributes, and Product Category are Location,Client Id,Client Secret,Product Category.

**Author**
**********

* BizzAppDev


**Used by**
***********

* BizzAppDev


**Installation**
****************

* Under applications, the application bad_connector_woocommerce can be installed/uninstalled.


**Configuration**
*****************

* Woo Backend:
    - Add configuration details such as the Location, version, Client Key, and Client Secret to sync with the database.

* Partners Import:
    - Navigate to Woocommerce Backends by going to Connectors > WooCommerce > WooCommerce Backends.
    - Add Backend Credentials to Import Partners.
    - Click 'Import Partners' button to Import the Partners from Woocommerce.
    - At the WooCommerce backend level, a new boolean option 'Allow Partners without Email' has been introduced. When this option is set to 'True', the system will import all partners from child_ids that do not have an email. Conversely, when the option is set to 'False', the system will import only those partners from child_ids that have an email.

* Products Import:
    - Navigate to Woocommerce Backends by going to Connectors > WooCommerce > WooCommerce Backends.
    - Add Backend Credentials to Import Products.
    - Click the 'Import Products' button to import Products from WooCommerce.
    - At the WooCommerce backend level, a new boolean option 'Allow Product without SKU' has been introduced. When this option is set to 'True', the system will import all Products from WooCommerce that do not have an SKU. Conversely, when the option is set to 'False', the system will import only those Products from WooCommerce that have an SKU.
    - At the WooCommerce backend level, in 'Advanced Configuration' tab there is 'Product Category' from that select any category in which you have to keep your Product.
    - Added a Price,Regular Price,Stock Status,Tax Status,WooCommerce Product Attribute Values, and Status at the binding level.
    - Added 'Product Category' field which is located at Connectors> WooCommerce > Advanced Configuration which is use to Set Odoo Product Category for imported WooCommerce Product.

* Product Attributes Import:
    - Navigate to Woocommerce Backends by going to Connectors > WooCommerce > WooCommerce Backends.
    - Add Backend Credentials to Import Product Attributes.
    - Click the 'Import Product Attributes' button to import Product Attributes from WooCommerce.
    - After Import Product Attribute immediately Attribute Value will be imported and another way to Import Attribute Value is Click the 'Import Attribute Value' button to import Product Attribute Values from WooCommerce.
    - The 'Product Attributes Value' menu item is located at Sale > Configuration > Product.
    - Product Attribute Value, add a "Group By" based on the Attribute.

* Product Categories Import:
    - Navigate to Woocommerce Backends by going to Connectors > WooCommerce > WooCommerce Backends.
    - Add Backend Credentials to Import Product Categories.
    - Click the 'Import Product Categories' button to import Product Categories from WooCommerce.
    - The 'WooCommerce Product Categories' menu item is located at Connector > WooCommerce > WooCommerce Product Categories.

* Orders Import:
    - - Navigate to Woocommerce Backends by going to Connectors > WooCommerce > WooCommerce Backends.
    - Add Backend Credentials to Import Orders.
    - Click 'Import Orders' button to Import the Orders from Woocommerce.


**Usage**
*********

* This module, 'Connector Woocommerce,' acts as a connector or integration tool for facilitating interaction between the Woocommerce platform and Odoo.

* Import of Partner Data:
  - Enable the import functionality in bad_connector_woocommerce to transfer partners from Woocommerce to Odoo.
  - Handle mapping of partner data at time of Import Partners.
  - Added filter base of binding.

* Import of Product Data:
  - Enable the import functionality in bad_connector_woocommerce to transfer products from WooCommerce to Odoo.
  - Handle mapping of product data during the import process.
  - Introduces "import_products_from_date" field at the backend level, allowing import from a specified date for getting updated products.
  - Implements import of Attributes and Categories during the product import.
  - Added woo_product_categ_ids and woo_attribute_ids in product binding level.

* Import of Product Attribute:
  - Enable the import functionality in bad_connector_woocommerce to transfer product Attributes from WooCommerce to Odoo.
  * Import of Product Attribute Value:
  - Enable the import functionality in bad_connector_woocommerce to transfer product Attribute Values from WooCommerce to Odoo.
  - Handle mapping of product attribute data during the import process.

* Import of Product Categories:
  - Enable the import functionality in bad_connector_woocommerce to transfer product Categories from WooCommerce to Odoo.
  - Handle mapping of product categories data during the import process.

* Import of Order Data:
  - Enable the import functionality in bad_connector_woocommerce to transfer Orders from Woocommerce to Odoo.
  - Handle mapping of sale order data at time of Import Orders.
  - Enable the form of Sale Order Line and added 'WooCommarce Connector' in sale order line level and added related line calculated field at binding level of sale oder line.
  - Added related sale order amount field at binding level of sale order.
  - Added 'Export Delivery Status' button at sale order level and it will export the Status of sale order to 'Completed' state and carrier_tracking_ref which is located at Stock Picking level in 'Additional info' tab.
  - At backend level,'Mark Order Completed On Delivery' boolean which is located at connectors > WooCommerce > Advanced Configuration tab if 'Mark Order Completed On Delivery' is True then 'Send Tracking Information' will be visible and if 'Mark Order Completed On Delivery' True then State will set 'Completed' in WooCommerce of that Order if 'Mark Order Completed On Delivery' and 'Send Tracking Information' then it will set Order to 'Completed' state and also tracking info will also send in WooCommerce.
  -When the Price Tax, recorded at the Order Line level, differs from the Total Tax Line value, recorded at the Order Line's binding level, a 'The WooCommerce Price Tax is different then Total Tax of Odoo.' Danger Banner will be displayed at the sale order level.
  -When the Amount Total, recorded at the Order level, differs from the woo Amount Total value, recorded at the Order binding level, a 'The WooCommerce Amount Total is different then Amount Total of Odoo.' Danger Banner will be displayed at the sale order level.

 -Mapping for Include tax.

**Known issues/Roadmap**
************************

* #N/A


**Changelog**
*************

* #N/A
