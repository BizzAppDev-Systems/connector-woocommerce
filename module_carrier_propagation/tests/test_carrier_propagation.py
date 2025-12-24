from odoo.tests.common import TransactionCase


class TestCarrierPropagation(TransactionCase):
    def setUp(self):
        super().setUp()
        # Create a delivery carrier
        self.carrier = self.env["delivery.carrier"].create(
            {
                "name": "Test Carrier",
                "fixed_price": 10.0,
            }
        )

        # Create a route with carrier
        self.route = self.env["stock.route"].create(
            {
                "name": "Test Route",
                "carrier_id": self.carrier.id,
            }
        )

        # Create a warehouse
        self.warehouse = self.env["stock.warehouse"].create(
            {
                "name": "Test Warehouse",
                "code": "TW",
            }
        )

        # Add route to warehouse
        self.warehouse.write({"route_ids": [(4, self.route.id)]})

        # Create a product
        self.product = self.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "product",
            }
        )

        # Create a picking type
        self.picking_type = self.env["stock.picking.type"].create(
            {
                "name": "Test Picking Type",
                "code": "outgoing",
                "warehouse_id": self.warehouse.id,
            }
        )

    def test_carrier_propagation(self):
        """Test that carrier is propagated from route to picking"""
        # Create a picking with route
        picking = self.env["stock.picking"].create(
            {
                "partner_id": self.env.ref("base.partner_demo").id,
                "picking_type_id": self.picking_type.id,
                "route_id": self.route.id,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom_qty": 1.0,
                            "product_uom": self.product.uom_id.id,
                            "location_id": self.warehouse.lot_stock_id.id,
                            "location_dest_id": self.env.ref(
                                "base.partner_demo"
                            ).property_stock_customer.id,
                        },
                    )
                ],
            }
        )

        # Check that carrier is set
        self.assertEqual(picking.carrier_id.id, self.carrier.id)

    def test_carrier_not_overridden(self):
        """Test that existing carrier is not overridden"""
        # Create another carrier
        carrier2 = self.env["delivery.carrier"].create(
            {
                "name": "Test Carrier 2",
                "fixed_price": 20.0,
            }
        )

        # Create a picking with route and explicit carrier
        picking = self.env["stock.picking"].create(
            {
                "partner_id": self.env.ref("base.partner_demo").id,
                "picking_type_id": self.picking_type.id,
                "route_id": self.route.id,
                "carrier_id": carrier2.id,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom_qty": 1.0,
                            "product_uom": self.product.uom_id.id,
                            "location_id": self.warehouse.lot_stock_id.id,
                            "location_dest_id": self.env.ref(
                                "base.partner_demo"
                            ).property_stock_customer.id,
                        },
                    )
                ],
            }
        )

        # Check that existing carrier is not overridden
        self.assertEqual(picking.carrier_id.id, carrier2.id)
