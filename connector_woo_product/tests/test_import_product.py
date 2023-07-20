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
