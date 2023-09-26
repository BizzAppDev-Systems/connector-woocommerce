from os.path import dirname, join

from vcr import VCR

from .test_woo_backend import BaseWooTestCase

recorder = VCR(
    cassette_library_dir=join(dirname(__file__), "fixtures/cassettes"),
    decode_compressed_response=True,
    filter_headers=["Authorization"],
    path_transformer=VCR.ensure_suffix(".yaml"),
    record_mode="once",
)


class TestImportProduct(BaseWooTestCase):
    def setUp(self):
        """Setup configuration for Product."""
        super().setUp()

    def test_import_product_product(self):
        """Test Assertions for Product"""
        external_id = "50"
        with recorder.use_cassette("import_woo_product_product"):
            self.env["woo.product.product"].import_record(
                external_id=external_id, backend=self.backend
            )
        product1 = self.env["woo.product.product"].search(
            [("external_id", "=", external_id)]
        )
        self.assertEqual(len(product1), 1)
        self.assertTrue(product1, "Woo Product is not imported!")
        self.assertEqual(
            product1.external_id, external_id, "External ID is different!!"
        )
        self.assertEqual(
            product1.name,
            "Shirt",
            "Product's name is not matched with response!",
        )
        self.assertEqual(
            product1.purchase_ok,
            False,
            "Purchase is not matched with response!",
        )
        self.assertEqual(
            product1.list_price,
            500,
            "List Price is not matched with response",
        )
        self.assertEqual(
            product1.default_code,
            "shirt-sku",
            "default_code is not match with response",
        )
        self.assertEqual(
            product1.price,
            "500",
            "Price is not matched with response",
        )
        self.assertEqual(
            product1.description,
            "<p>shirt.</p>\n",
            "description is not matched with response",
        )
        self.assertEqual(
            product1.regular_price,
            "599",
            "regular price is not matched with response",
        )
        self.assertEqual(
            product1.status,
            "publish",
            "status is not matched with response",
        )
        self.assertEqual(
            product1.tax_status,
            "taxable",
            "tax status is not matched with response",
        )
        self.assertEqual(
            product1.stock_status,
            "instock",
            "stock status is not matched with response",
        )
