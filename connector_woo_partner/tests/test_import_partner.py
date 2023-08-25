from os.path import dirname, join

from vcr import VCR

from odoo.addons.connector_woo_base.tests.test_woo_backend import BaseWooTestCase

recorder = VCR(
    cassette_library_dir=join(dirname(__file__), "fixtures/cassettes"),
    decode_compressed_response=True,
    filter_headers=["Authorization"],
    path_transformer=VCR.ensure_suffix(".yaml"),
    record_mode="once",
)


class TestImportPartner(BaseWooTestCase):
    def setUp(self):
        """Setup configuration for Partner."""
        super().setUp()

    def test_import_res_partner(self):
        """Test Assertions for Partner"""
        with recorder.use_cassette("import_woo_res_partner"):
            self.env["woo.res.partner"].import_record(
                external_id="237660088", backend=self.backend
            )
        external_id = "237660088"
        self.partner_model = self.env["woo.res.partner"]
        partner1 = self.partner_model.search([("external_id", "=", external_id)])
        self.assertEqual(len(partner1), 1)
        self.assertTrue(partner1, "Woo Partner is not imported!")
        self.assertEqual(
            partner1.external_id, external_id, "External ID is different!!"
        )
        self.assertEqual(
            partner1.firstname,
            "Siddhi",
            "Partner's First name is not matched with response!",
        )
        self.assertEqual(
            partner1.lastname,
            "padiya",
            "Partner's Last name is not matched with response!",
        )
        self.assertEqual(
            partner1.name,
            "Siddhi padiya",
            "Partner's name is not matched with response!",
        )
        self.assertEqual(
            partner1.email,
            "siddhi.padiya@gmail.com",
            "Partner's Email is not matched with response!",
        )
