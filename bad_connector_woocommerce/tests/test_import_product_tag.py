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


class TestImportProductTag(BaseWooTestCase):
    def setUp(self):
        """Setup configuration for Product Tag."""
        super().setUp()

    def test_import_product_tag(self):
        """Test Assertions for Product Tag"""
