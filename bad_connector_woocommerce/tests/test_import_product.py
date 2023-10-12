import requests
from PIL import Image
from io import BytesIO
from os.path import dirname, join

from vcr import VCR

# from ...components import utils
from .test_woo_backend import BaseWooTestCase

recorder = VCR(
    cassette_library_dir=join(dirname(__file__), "fixtures/cassettes"),
    decode_compressed_response=True,
    filter_headers=["Authorization"],
    path_transformer=VCR.ensure_suffix(".yaml"),
    record_mode="once",
)
# B64_PNG_IMG_4PX_GREEN = "iVBORw0KGgoAAAANSUhEUgAAAAQAAAAECAIAAAAmkwkpAAAAmElEQVR42mJ88MAEnZBVzWDFSpAjTGnCEjG4MUqQMkxpxIbPXIqUMYxRMAjpQLM1hCkwRgCBNRiE5RlV9jAAAAAElFTkSuQmCC"


class TestImportProduct(BaseWooTestCase):
    def setUp(self):
        """Setup configuration for Product."""
        super().setUp()

    # def download_image(self, image_url, product1):
    #     try:
    #         response = requests.get(image_url)
    #         response.raise_for_status()

    #         # Check if the response contains image data
    #         if "image" in response.headers["Content-Type"]:
    #             # Save the image data to the image_1920 field
    #             image = Image.open(BytesIO(response.content))
    #             product1.image_1920 = image.tobytes()
    #     except requests.exceptions.RequestException as e:
    #         print(f"Error downloading image: {e}")

    def test_import_product_product(self):
        """Test Assertions for Product"""
        external_id = "50"
        with recorder.use_cassette("import_woo_product_product"):
            self.env["woo.product.product"].import_record(
                external_id=external_id, backend=self.backend
            )
        product1 = self.env["woo.product.product"].search(
            [("external_id", "=", external_id)]
        )
        self.assertEqual(len(product1), 1)
        self.assertTrue(product1, "Woo Product is not imported!")
        self.assertEqual(
            product1.external_id, external_id, "External ID is different!!"
        )
        self.assertEqual(
            product1.name,
            "Shirt",
            "Product's name is not matched with response!",
        )
        self.assertEqual(
            product1.purchase_ok,
            False,
            "Purchase is not matched with response!",
        )
        self.assertEqual(
            product1.list_price,
            500,
            "List Price is not matched with response",
        )
        self.assertEqual(
            product1.default_code,
            "shirt-sku",
            "default_code is not match with response",
        )
        self.assertEqual(
            product1.price,
            "500",
            "Price is not matched with response",
        )
        self.assertEqual(
            product1.description,
            "<p>shirt.</p>\n",
            "description is not matched with response",
        )
        self.assertEqual(
            product1.regular_price,
            "599",
            "regular price is not matched with response",
        )
        self.assertEqual(
            product1.status,
            "publish",
            "status is not matched with response",
        )
        self.assertEqual(
            product1.tax_status,
            "taxable",
            "tax status is not matched with response",
        )
        self.assertEqual(
            product1.stock_status,
            "instock",
            "stock status is not matched with response",
        )
        self.assertEqual(
            product1.detailed_type,
            self.backend.default_product_type,
            "Product Type is not matched with response.",
        )
        # self.assertEqual(len(product1.woo_product_image_url_ids), 1)
        # Check if the image is created in woo.product.image.url
        # image_url = (
        #     "http://localhost:8081/wp-content/uploads/2023/10/parth_timesheet.png"
        # )
        # image_name = "parth_timesheet"
        # image = self.env["woo.product.image.url"].search(
        #     [("url", "=", image_url), ("name", "=", image_name)]
        # )
        # self.assertTrue(image, "Image is not created in woo.product.image.url!")

        # Check if the product's image_1920 field is populated with binary data
        # self.download_image(
        #     "https://woo-wildly-inner-cycle.wpcomstaging.com/wp-content/uploads/2023/09/pennant-1.jpg",
        #     product1,
        # )
        # self.assertTrue(
        #     product1.image_1920, "image_1920 field is not populated with binary data!"
        # )
        # Download and store the primary image

    #     primary_image_url = "http://localhost:9100/media/catalog/product/i/n/ink-eater-krylon-bombear-destroyed-tee-1.jpg"
    #     primary_image_name = "ink-eater-krylon-bombear-destroyed-tee-1.jpg"
    #     self.download_and_store_image(product1, primary_image_url, primary_image_name)

    #     # Download and store other images
    #     images_payload = [
    #         {
    #             "exclude": "1",
    #             "file": "/i/n/ink-eater-krylon-bombear-destroyed-tee-1.jpg",
    #             "label": "",
    #             "position": "0",
    #             "types": ["thumbnail"],
    #             "url": "http://localhost:9100/media/catalog/product/i/n/ink-eater-krylon-bombear-destroyed-tee-1.jpg",
    #         },
    #         # Add more image entries here as needed
    #     ]

    #     for image_entry in images_payload:
    #         if "url" in image_entry and "file" in image_entry:
    #             image_name = image_entry["file"].split("/")[-1]
    #             image_url = image_entry["url"]
    #             self.download_and_store_image(product1, image_url, image_name)

    # def download_and_store_image(self, product, image_url, image_name):
    #     binary_data = utils.fetch_image_data(image_url)
    #     if binary_data:
    #         product.image_1920 = binary_data

    #         # Store the image URL in the woo.product.image.url object
    #         self.env["woo.product.image.url"].create(
    #             {
    #                 "name": image_name,
    #                 "url": image_url,
    #             }
    #         )
