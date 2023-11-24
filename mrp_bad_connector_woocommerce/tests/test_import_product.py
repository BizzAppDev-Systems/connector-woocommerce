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

    def test_import_product_product_grouped_type(self):
        """Test Assertions for Grouped type Product"""
        external_id = "168"
        with recorder.use_cassette("import_woo_product_product"):
            self.env["woo.product.product"].import_record(
                external_id=external_id, backend=self.backend
            )
        product1 = self.env["woo.product.product"].search(
            [("external_id", "=", external_id)], limit=1
        )
        self.assertTrue(product1, "Woo Product is not imported!")
        self.assertTrue(product1.bom_ids, "No BOM is created for the imported product!")
