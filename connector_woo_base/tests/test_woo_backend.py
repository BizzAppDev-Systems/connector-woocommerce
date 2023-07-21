from odoo.addons.component.tests.common import TransactionComponentCase


class BaseWooTestCase(TransactionComponentCase):
    def setUp(self):
        """Set up for backend"""
        super().setUp()
        self.backend_record = self.env["woo.backend"]
        self.backend = self.backend_record.create(
            {
                "name": "Test Woo Backend",
                "default_limit": 10,
                "company_id": self.env.company.id,
                "version": "v3",
                "test_mode": True,
                "test_location": "https://woo-wildly-inner-cycle.wpcomstaging.com",
                "test_client_id": "ck_0e98f5d84573948942454e07e899c1e0f3bfd7cf",
                "test_client_secret": "cs_c2e24b2662280a0a1a6cae494d9c9b2e05d5c139",
            }
        )
        self.backend_data = {
            "name": "Woo Backend",
            "default_limit": 10,
            "company_id": self.env.company.id,
            "version": "v3",
            "test_mode": False,
            "location": "https://woo-wildly-inner-cycle.wpcomstaging.com",
            "client_id": "ck_0e98f5d84573948942454e07e899c1e0f3bfd7cf",
            "client_secret": "cs_c2e24b2662280a0a1a6cae494d9c9b2e05d5c139",
        }

    def test_backend_test_mode_true(self):
        """Test case for backend with test_mode True"""
        self.assertEqual(self.backend.test_mode, True)
        self.assertEqual(self.backend.version, "v3")
        self.assertEqual(
            self.backend.test_location,
            "https://woo-wildly-inner-cycle.wpcomstaging.com",
        )
        self.assertEqual(
            self.backend.test_client_id, "ck_0e98f5d84573948942454e07e899c1e0f3bfd7cf"
        )
        self.assertEqual(
            self.backend.test_client_secret,
            "cs_c2e24b2662280a0a1a6cae494d9c9b2e05d5c139",
        )

    def test_backend_test_mode_false(self):
        """Test case for backend with test_mode False"""
        self.backend = self.env["woo.backend"].create(self.backend_data)
        self.assertEqual(self.backend.test_mode, False)
        self.assertEqual(self.backend.version, "v3")
        self.assertEqual(
            self.backend.location, "https://woo-wildly-inner-cycle.wpcomstaging.com"
        )
        self.assertEqual(
            self.backend.client_id, "ck_0e98f5d84573948942454e07e899c1e0f3bfd7cf"
        )
        self.assertEqual(
            self.backend.client_secret, "cs_c2e24b2662280a0a1a6cae494d9c9b2e05d5c139"
        )
