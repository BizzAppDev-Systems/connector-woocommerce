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


class TestImportCountry(BaseWooTestCase):
    def setUp(self):
        """Setup configuration for Country."""
        super().setUp()

    def test_import_res_country_without_name(self):
        """Test Country without code"""
        external_id = "po"
        with recorder.use_cassette("import_country_without_name"):
            self.env["woo.res.country"].import_record(
                external_id=external_id, backend=self.backend
            )
        self.country_model = self.env["woo.res.country"]
        country1 = self.country_model.search([("external_id", "=", external_id)])
        self.assertEqual(len(country1), 1)
