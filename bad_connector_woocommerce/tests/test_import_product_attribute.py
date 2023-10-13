from os.path import dirname, join

from vcr import VCR
from odoo.addons.queue_job.tests.common import trap_jobs
from .test_woo_backend import BaseWooTestCase

recorder = VCR(
    cassette_library_dir=join(dirname(__file__), "fixtures/cassettes"),
    decode_compressed_response=True,
    filter_headers=["Authorization"],
    path_transformer=VCR.ensure_suffix(".yaml"),
    record_mode="once",
)


class TestImportProductAttributes(BaseWooTestCase):
    def setUp(self):
        """Setup configuration for Product Attribute."""
        super().setUp()

    def test_import_product_attribute(self):
        """Test Assertions for Product Attribute"""
        external_id = "2"
        with recorder.use_cassette("import_woo_product_attribute"):
            self.env["woo.product.attribute"].import_record(
                external_id=external_id, backend=self.backend
            )
        self.product_model = self.env["woo.product.attribute"]
        productattribute1 = self.product_model.search(
            [("external_id", "=", external_id)]
        )
        self.assertEqual(len(productattribute1), 1)
        self.assertTrue(productattribute1, "Woo Product Attribute is not imported!")
        self.assertEqual(
            productattribute1.external_id, external_id, "External ID is different!!"
        )
        self.assertEqual(
            productattribute1.name,
            "colour",
            "Product Attribute name is not matched with response!",
        )
        self.assertEqual(
            productattribute1.has_archives,
            False,
            "has_archives is not match with response",
        )
        with recorder.use_cassette("import_product_attribute_value"):
            with trap_jobs() as trap:
                external_id = "32"
                filters = {}
                filters.update(
                    {
                        "attribute": external_id,
                    }
                )
                self.backend._sync_from_date(
                    model="woo.product.attribute.value",
                    export=False,
                    filters=filters,
                )
                # Assert that how many queuejobs are being prepared.
                trap.assert_jobs_count(1)
                # And then skip enqueued jobs
                trap.perform_enqueued_jobs()
                trap.assert_jobs_count(3)
                trap.perform_enqueued_jobs()
        # Searching record for res.partner with unique external id to check record
        # created or not.
        # parent = self.env["test.res.partner"].search(
        #     [
        #         ("external_id", "=", "1111"),
        #         (
        #             "backend_id",
        #             "=",
        #             self.backend.id,
        #         ),
        #     ]
        # )
        # child = self.env["test.res.partner"].search(
        #     [
        #         ("external_id", "=", "0000"),
        #         (
        #             "backend_id",
        #             "=",
        #             self.backend.id,
        #         ),
        #     ]
        # )
        # country = self.env["test.res.country"].search(
        #     [
        #         ("external_id", "=", 1212),
        #         (
        #             "backend_id",
        #             "=",
        #             self.backend.id,
        #         ),
        #     ]
        # )
        # # Assert for partner creation using run method.
        # self.assertTrue(parent, "Parent did not created!")
        # self.assertTrue(child, "Child did not created!")
        # self.assertTrue(country, "Country did not created!")
        # print("helllllllllllllllllloooooooooooooo")
        # productattribute1.sync_attribute_values_from_woo()
        # print(productattribute1.sync_attribute_values_from_woo(), "=============")
