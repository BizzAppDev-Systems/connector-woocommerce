**Connector Woo Product**
=========================

**Description**
***************

* Technical name: connector_woo_product.
* Create a module named connector_woo_product that extends the functionality of connector_woo_base.
  This module focuses on the import and export of Product data between Woocommerce and Odoo.
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
    - Go to Woocommerce Backends.
    - Add Backend Credentils to Import Products.
    - Click 'Import Products' button to Import the Products from Woocommerce.
* Product Attributes Import:
    - Go to Woocommerce Backends.
    - Add Backend Credentils to Import Product Attributes.
    - Click 'Import Product Attributes' button to Import the Product Attributes from Woocommerce.
    - Click 'Import Attribute Value' button to Import the Product Attributes Value from Woocommerce.
* Product Categories Import:
    - Go to Woocommerce Backends.
    - Add Backend Credentils to Import Product categories.
    - Click 'Import Product Categories' button to Import the Product Categories from Woocommerce.


**Usage**
*********

* Import of Product Data:
  - Enable the import functionality in connector_woo_product to transfer products from Woocommerce to Odoo.
  - Handle mapping of product data at time of Import Products.
  - Added "import_products_from_date" field at backend level which implements the functionality of import from date which helps to get the updated product according to selected date.
  - Implemented import Attribute and import category at time of import product.
* Import of Product Attribute:
  - Enable the import functionality in connector_woo_product to transfer product Attributes from Woocommerce to Odoo.
  * Import of Product Attribute Value:
  - Enable the import functionality in connector_woo_product to transfer product Attributes Value from Woocommerce to Odoo.
  - Handle mapping of product attribute data at time of Import Products.
* Import of Product Category:
  - Enable the import functionality in connector_woo_product to transfer product Categories from Woocommerce to Odoo.
  - Handle mapping of product category data at time of Import Products.


**Known issues/Roadmap**
************************

* #N/A


**Changelog**
*************

* #N/A
