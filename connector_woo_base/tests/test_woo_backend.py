from odoo.tests.common import TransactionCase


class TestWooBackend(TransactionCase):
    def setUp(self):
        """Set up for backend"""
        super().setUp()
        self.backend_data_test = {
            "name": "Test Woo Backend",
            "default_limit": 10,
            "company_id": self.env.company.id,
            "version": "v3",
            "test_mode": True,
            "test_location": "https://woo-test.com",
            "test_client_id": "ck_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "test_client_secret": "cs_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        }
        self.backend_data = {
            "name": "Woo Backend",
            "default_limit": 10,
            "company_id": self.env.company.id,
            "version": "v3",
            "test_mode": False,
            "location": "https://woo-test.com",
            "client_id": "ck_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "client_secret": "cs_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        }

    def test_backend_test_mode_true(self):
        """Test case for backend with test_mode True"""
        self.backend = self.env["woo.backend"].create(self.backend_data_test)
        self.assertEqual(self.backend.test_mode, True)
        self.assertEqual(self.backend.version, "v3")
        self.assertEqual(self.backend.test_location, "https://woo-test.com")
        self.assertEqual(
            self.backend.test_client_id, "ck_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        )
        self.assertEqual(
            self.backend.test_client_secret, "cs_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        )

    def test_backend_test_mode_false(self):
        """Test case for backend with test_mode False"""
        self.backend = self.env["woo.backend"].create(self.backend_data)
        self.assertEqual(self.backend.test_mode, False)
        self.assertEqual(self.backend.version, "v3")
        self.assertEqual(self.backend.location, "https://woo-test.com")
        self.assertEqual(
            self.backend.client_id, "ck_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        )
        self.assertEqual(
            self.backend.client_secret, "cs_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        )
