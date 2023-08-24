**Connector Woo Product**
=========================

**Description**
***************

* Technical name: connector_woo_product.
* This module extends the functionality of connector_woo_base and focuses on importing and exporting Product data between WooCommerce and Odoo.
* It provides options to import "Products," "Product Attributes," and "Product Categories" at the backend level.
* Add "Import Products","Import Product Attributes" and "Import Product Category" at backend level.
* Required field to Import the Products,Product Attributes, and Product Category are Location,Client Id,Client Secret.


**Author**
**********

* BizzAppDev


**Used by**
***********

* #N/A


**Installation**
****************

* Under applications, the application connector_woo_product can be installed/uninstalled.


**Configuration**
*****************

* Products Import:
    - Navigate to WooCommerce Backends.
    - Add Backend Credentials to Import Products.
    - Click the 'Import Products' button to import Products from WooCommerce.

* Product Attributes Import:
    - Navigate to WooCommerce Backends.
    - Add Backend Credentials to Import Product Attributes.
    - Click the 'Import Product Attributes' button to import Product Attributes from WooCommerce.
    - Click the 'Import Attribute Value' button to import Product Attribute Values from WooCommerce.
    - The 'Product Attributes Value' menu item is located at Sale > Configuration > Product.

* Product Categories Import:
    - Navigate to WooCommerce Backends.
    - Add Backend Credentials to Import Product Categories.
    - Click the 'Import Product Categories' button to import Product Categories from WooCommerce.
    - The 'WooCommerce Product Categories' menu item is located at Connector > Woo Product Categories > Product Categories.


**Usage**
*********

* Import of Product Data:
  - Enable the import functionality in connector_woo_product to transfer products from WooCommerce to Odoo.
  - Handle mapping of product data during the import process.
  - Introduces "import_products_from_date" field at the backend level, allowing import from a specified date for getting updated products.
  - Implements import of Attributes and Categories during the product import.

* Import of Product Attribute:
  - Enable the import functionality in connector_woo_product to transfer product Attributes from WooCommerce to Odoo.
  * Import of Product Attribute Value:
  - Enable the import functionality in connector_woo_product to transfer product Attribute Values from WooCommerce to Odoo.
  - Handle mapping of product attribute data during the import process.

* Import of Product Categories:
  - Enable the import functionality in connector_woo_product to transfer product Categories from WooCommerce to Odoo.
  - Handle mapping of product categories data during the import process.


**Known issues/Roadmap**
************************

* #N/A


**Changelog**
*************

* #N/A
