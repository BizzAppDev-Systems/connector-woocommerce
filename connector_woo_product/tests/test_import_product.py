from .common import WooTestCase, recorder


class TestImportProduct(WooTestCase):
    def setUp(self):
        """Setup configuration for Product."""
        super().setUp()

    @recorder.use_cassette
    def test_import_product_product(self):
        """Test Assertions for Product"""
        self._import_record(
            "woo.product.product",
            external_id="56",
        )
        external_id = "56"
        self.product_model = self.env["woo.product.product"]
        product1 = self.product_model.search([("external_id", "=", external_id)])
        self.assertEqual(len(product1), 1)
        self.assertTrue(product1, "Woo Product is not imported!")
        self.assertEqual(
            product1.external_id, external_id, "External ID is different!!"
        )
        self.assertEqual(
            product1.name,
            "Product",
            "Product's name is not matched with response!",
        )
        self.assertEqual(
            product1.sale_ok,
            False,
            "Sale is not matched with response!",
        )
        self.assertEqual(
            product1.purchase_ok,
            False,
            "Purchase is not matched with response!",
        )
        self.assertEqual(
            product1.list_price,
            50,
            "List Price is not matched with response",
        )
        self.assertEqual(
            product1.default_code,
            "product_sku",
            "default_code is not match with response",
        )
