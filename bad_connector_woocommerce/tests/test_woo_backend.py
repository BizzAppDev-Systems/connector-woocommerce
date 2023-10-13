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
                "version": "wc/v3",
                "test_mode": True,
                "product_categ_id": self.env.ref("product.product_category_all").id,
                "test_location": "https://woo-wildly-inner-cycle.wpcomstaging.com",
                "test_client_id": "ck_0e98f5d84573948942454e07e899c1e0f3bfd7cf",
                "test_client_secret": "cs_c2e24b2662280a0a1a6cae494d9c9b2e05d5c139",
                "default_product_type": "product",
                "default_carrier_product_id": self.env.ref(
                    "product.expense_product"
                ).id,
            }
        )
        self.backend_data = {
            "name": "Woo Backend",
            "default_limit": 10,
            "company_id": self.env.company.id,
            "version": "wc/v3",
            "test_mode": False,
            "product_categ_id": self.env.ref("product.product_category_all").id,
            "location": "https://woo-wildly-inner-cycle.wpcomstaging.com",
            "client_id": "ck_0e98f5d84573948942454e07e899c1e0f3bfd7cf",
            "client_secret": "cs_c2e24b2662280a0a1a6cae494d9c9b2e05d5c139",
            "default_product_type": "product",
            "default_carrier_product_id": self.env.ref("product.expense_product").id,
        }

    def test_backend_test_mode_true(self):
        """Test case for backend with test_mode True"""
        self.assertEqual(self.backend.test_mode, True)
        self.assertEqual(self.backend.version, "wc/v3")
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
        self.assertEqual(self.backend.version, "wc/v3")
        self.assertEqual(
            self.backend.location, "https://woo-wildly-inner-cycle.wpcomstaging.com"
        )
        self.assertEqual(
            self.backend.client_id, "ck_0e98f5d84573948942454e07e899c1e0f3bfd7cf"
        )
        self.assertEqual(
            self.backend.client_secret, "cs_c2e24b2662280a0a1a6cae494d9c9b2e05d5c139"
        )

    def test_toggle_test_mode(self):
        """Test case for toggle_test_mode method"""
        # Initial state should be True
        self.assertEqual(self.backend.test_mode, True)

        # Call the toggle_test_mode method
        self.backend.toggle_test_mode()

        # Check if the test_mode is now False
        self.assertEqual(self.backend.test_mode, False)

        # Call the toggle_test_mode method again
        self.backend.toggle_test_mode()

        # Check if the test_mode is now True again
        self.assertEqual(self.backend.test_mode, True)
