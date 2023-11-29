Sale Order Status Export
========================

In this section, we will explore the functionality of the exporting the Sale order status with tracking reference from odoo to Woocommerce.

Advance Configurations to export status
---------------------------------------

In advance configurations of sale order there are two boolean fields.

1. Mark Order Completed On Delivery
2. Send Tracking Information

.. image:: _static/ order_status_config.png
   :align: center

* Note: The 'Send Tracking Information' option will only be visible when the 'Mark Order Completed On Delivery' option is set to 'True'.

Case 1: Mark Order Completed Is False
*************************************

After following the basic flow of confirming sale order and validating the delivery order in odoo we can see a button called "EXPORT DELIVERY STATUS" will be visible.

.. image:: _static/ export_status_botton.png
   :align: center

* As we are considering the case of 'Mark Order Completed On Delivery' option in woocommerce backend is NOT True we will get the message while trying to export the status.

.. image:: _static/ validation_on_status_export.png
   :align: center

Case 2: Mark Order Completed Is True
************************************

As we are considering the case of 'Mark Order Completed On Delivery' option in woocommerce backend set to 'True' we will able to export the status successfully.

* Currently Woocommerce Status is in 'Processing' Stage:

.. image:: _static/ export_status_botton.png
   :align: center

* After clicking on "EXPORT DELIVERY STATUS" Woocommerce Status is changes to 'Completed' Stage:

.. image:: _static/ status_updated_sale.png
   :align: center

* Woocommerce Order status before:

.. image:: _static/ before_status_update.png
   :align: center

* Woocommerce Order status after:

.. image:: _static/ after_status_update.png
   :align: center


Case 3: Mark Order Completed Is True and Send Tracking Information Is True
**************************************************************************

.. image:: _static/ both_true.png
   :align: center

Now we are understanding the case of exporting sale order status with tracking reference.

* We will follow the normal flow of creating delivery order from sale order.

.. image:: _static/ confirm_button_sale_order.png
   :align: center

**Note**: There can be two sub cases while validating the delivery order:

   1) Delivery order without tracking reference
   2) Delivery order with tracking reference

**Scenario 1 : Validating delivery order without Tracking Reference**

.. image:: _static/ delivery_without_tracking.png
   :align: center

* The Validation message of "Tracking Reference not found" will be visible at the time of exporting the status of sale order as we did not provided value in tracking reference field.

.. image:: _static/ validation_of_no_tracking.png
   :align: center

**Scenario 2 : Validating delivery order with Tracking Reference**

.. image:: _static/ delivery_with_tracking.png
   :align: center

* The normal flow of export status will work and send the order status along with tracking reference.

.. image:: _static/ final_sale_order.png
   :align: center
