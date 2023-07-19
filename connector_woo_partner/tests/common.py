from os.path import dirname, join

from vcr import VCR

from odoo.addons.component.tests.common import TransactionComponentCase

recorder = VCR(
    cassette_library_dir=join(dirname(__file__), "fixtures/cassettes"),
    decode_compressed_response=True,
    filter_headers=["Authorization"],
    path_transformer=VCR.ensure_suffix(".yaml"),
    record_mode="once",
)


class WooTestCase(TransactionComponentCase):
    def setUp(self):
        """Configurations for backend."""
        super().setUp()
        self.recorder = recorder
        self.backend_record = self.env["woo.backend"]
        self.backend = self.backend_record.create(
            {
                "name": "Test Woo Backend",
                "default_limit": 1,
                "company_id": self.env.company.id,
                "version": "v3",
                "test_mode": True,
                "test_location": "https://woo-wildly-inner-cycle.wpcomstaging.com",
                "test_client_id": "ck_0e98f5d84573948942454e07e899c1e0f3bfd7cf",
                "test_client_secret": "cs_c2e24b2662280a0a1a6cae494d9c9b2e05d5c139",
            }
        )

    def _import_record(
        self,
        model_name,
        external_id=None,
        filters=None,
        data=None,
        force=False,
        cassette=True,
    ):
        """Configuration before importing the record."""
        assert model_name.startswith("woo.")
        table_name = model_name.replace(".", "_")
        filename = "import_%s" % (table_name)

        def run_import_record():
            self.env[model_name].import_record(
                backend=self.backend, external_id=external_id, data=data
            )

        if cassette:
            with self.recorder.use_cassette(filename):
                run_import_record()
