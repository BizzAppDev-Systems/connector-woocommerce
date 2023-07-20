from .common import WooTestCase, recorder


class TestImportPartner(WooTestCase):
    def setUp(self):
        """Setup configuration for Partner."""
        super().setUp()

    @recorder.use_cassette
    def test_import_res_partner(self):
        """Test Assertions for Partner"""
        self._import_record(
            "woo.res.partner",
            external_id="237660088",
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
            partner1.name,
            "siddhi padiya",
            "Partner's name is not matched with response!",
        )
        self.assertEqual(
            partner1.email,
            "siddhi.padiya@gmail.com",
            "Partner's Email is not matched with response!",
        )
