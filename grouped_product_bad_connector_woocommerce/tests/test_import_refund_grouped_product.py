from os.path import dirname, join

from vcr import VCR

from ...bad_connector_woocommerce.tests.test_woo_backend import BaseWooTestCase

recorder = VCR(
    cassette_library_dir=join(dirname(__file__), "fixtures/cassettes"),
    decode_compressed_response=True,
    filter_headers=["Authorization"],
    path_transformer=VCR.ensure_suffix(".yaml"),
    record_mode="once",
)


class TestImportGroupedProductRefund(BaseWooTestCase):
    def setUp(self):
        """Setup configuration for Sale order grouped product refund."""
        super().setUp()

    def test_import_order_for_grouped_product_refund(self):
        """Test Assertions for Import refund"""
        external_id = "71"

        with recorder.use_cassette("import_woo_product_product"):
            self.env["woo.sale.order"].import_record(
                external_id=external_id, backend=self.backend
            )
        sale_order1 = self.env["woo.sale.order"].search(
            [("external_id", "=", external_id)]
        )
        self.assertEqual(len(sale_order1), 1)

        self.assertTrue(sale_order1, "Woo Sale Order is not imported!")
        self.assertEqual(
            sale_order1.external_id, external_id, "External ID is different!!"
        )
        self.assertEqual(
            sale_order1.name,
            "WOO_71",
            "Order's name is not matched with response!",
        )
        self.assertEqual(
            sale_order1.woo_order_status_id.code,
            "processing",
            "Order's status is not matched with response!",
        )
        sale_order_odoo = self.env["sale.order"].search(
            [("name", "=", "WOO_71")], limit=1
        )
        sale_order_odoo.action_confirm()
        delivery_order = sale_order_odoo.picking_ids
        self.assertTrue(delivery_order, "Delivery order not created for the sale order")
        delivery_order.move_ids[0].quantity = 1
        delivery_order.button_validate()
        self.assertEqual(
            sale_order1.picking_ids[0].state, "done", "Picking state should be done!"
        )
        self.backend.process_return_automatically = True
        with recorder.use_cassette("import_woo_order_refund"):
            kwargs = {}
            kwargs["order_id"] = 71
            kwargs["refund_order_status"] = "refunded"
            self.env["woo.stock.picking.refund"].import_record(
                external_id="1481", backend=self.backend, **kwargs
            )
        self.assertEqual(
            sale_order_odoo.woo_order_status_id.code,
            "refunded",
            "Sale Order is Not in 'Refunded' state in WooCommerce.",
        )
        self.assertEqual(len(sale_order_odoo.picking_ids), 2)
