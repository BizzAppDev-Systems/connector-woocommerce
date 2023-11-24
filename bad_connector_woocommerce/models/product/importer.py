import logging

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create
from odoo.addons.connector.exception import MappingError

from ...components import utils

# pylint: disable=W7950

_logger = logging.getLogger(__name__)


class WooProductProductBatchImporter(Component):
    """Batch Importer the WooCommerce Product"""

    _name = "woo.product.product.batch.importer"
    _inherit = "woo.delayed.batch.importer"
    _apply_on = "woo.product.product"


class WooProductImageUrlImporter(Component):
    """
    Import translations for a record.

    Usually called from importers, in ``_after_import``.
    For instance from the products and products' Image importers.
    This importer is responsible for fetching image data from an external
    source based on the provided image URL.
    """

    _name = "woo.product.image.url.importer"
    _inherit = "woo.importer"
    _usage = "product.image.importer"

    def run(self, external_id, binding, image_data):
        """
        Import and associate product images.
        :param image_data: List of image information.
        """
        image_ids = []
        for index, image_info in enumerate(image_data):
            if index == 0:
                image_record = self._import_primary_image(binding, image_info)
            else:
                image_record = self._import_secondary_image(image_info)
            image_ids.append(image_record.id)
        if image_ids:
            binding.write({"woo_product_image_url_ids": [(6, 0, image_ids)]})

    def _find_existing_image(self, name, url):
        """
        Find an existing image record based on name and URL.
        :param name: The name of the image.
        :param url: The URL of the image.
        :return: Existing image record or None if not found.
        """
        return self.env["woo.product.image.url"].search(
            [("name", "=", name), ("url", "=", url)], limit=1
        )

    def _import_primary_image(self, binding, image_info):
        """
        Import primary product image.
        :param image_info: Information about the primary image.
        """
        name = image_info.get("name")
        image_url = image_info.get("src")
        alt = image_info.get("alt")
        image_record = self._find_existing_image(name, image_url)
        if not image_record:
            image_values = {
                "name": name,
                "url": image_url,
                "alt": alt,
            }
            image_record = self.env["woo.product.image.url"].create(image_values)
        binary_data = utils.fetch_image_data(image_url)
        if not binary_data:
            return image_record
        binding.write({"image_1920": binary_data})
        return image_record

    def _import_secondary_image(self, image_info):
        """
        Get or create a secondary image record.
        :param image_info: Information about the secondary image.
        :return: Secondary image record.
        """
        name = image_info.get("name")
        url = image_info.get("src")
        alt = image_info.get("alt")
        existing_image = self._find_existing_image(name, url)
        image_values = {
            "name": name,
            "url": url,
            "alt": alt,
        }
        if not existing_image:
            return self.env["woo.product.image.url"].create(image_values)
        return existing_image


class WooProductProductImportMapper(Component):
    """Impoter Mapper for the WooCommerce Product"""

    _name = "woo.product.product.import.mapper"
    _inherit = "woo.product.common.mapper"
    _apply_on = "woo.product.product"

    @only_create
    @mapping
    def odoo_id(self, record):
        """Mapping for odoo id"""
        if record.get("type") != "variation":
            return {}
        binder = self.binder_for("woo.product.template")
        # Extract attributes from the WooCommerce product variant data
        attributes = record.get("attributes", [])
        attribute_dict = {attr["name"]: attr["option"] for attr in attributes}

        # Find the Odoo product variant with matching attributes
        template_id = binder.to_internal(record.get("parent_id"), unwrap=True)
        odoo_variants = template_id.product_variant_ids
        matching_variant = None

        for variant in odoo_variants:
            variant_attributes = {
                attr_vals.attribute_id.name: attr_vals.name
                for attr_vals in variant.product_template_attribute_value_ids
            }
            if variant_attributes != attribute_dict:
                continue
            matching_variant = variant
            break

        return {"odoo_id": matching_variant.id} if matching_variant else {}

    @mapping
    def woo_product_name(self, record):
        """Mapping for woo_product_name"""
        name = record.get("name")
        if not name:
            raise MappingError(
                _("Product name doesn't exist for Product ID %s Please check")
                % record.get("id")
            )
        return {"woo_product_name": name}

    @mapping
    def default_code(self, record):
        """Mapped product default code."""
        default_code = record.get("sku")
        if not default_code and not self.backend_record.without_sku:
            raise MappingError(
                _("SKU is Missing for the product '%s' !", record.get("name"))
            )
        return {"default_code": default_code} if default_code else {}

    @mapping
    def product_tmpl_id(self, record):
        """Mapping for product_tmpl_id"""
        binder = self.binder_for("woo.product.template")
        template_id = binder.to_internal(record.get("parent_id"), unwrap=True)
        return {"product_tmpl_id": template_id.id} if template_id else {}

    @mapping
    def active(self, record):
        """Mapping for active"""
        return {"active": True}


class WooProductProductImporter(Component):
    """Importer the WooCommerce Product"""

    _name = "woo.product.product.importer"
    _inherit = "woo.importer"
    _apply_on = "woo.product.product"

    def _after_import(self, binding, **kwargs):
        """
        This method is Overrides the default behavior of _after_import when importing
        images from a remote record. If no image records are found in the remote record,
        it returns the result of the super class's '_after_import' method.
        """
        result = super(WooProductProductImporter, self)._after_import(binding, **kwargs)
        image_record = self.remote_record.get("images")
        if not image_record:
            return result
        image_importer = self.component(usage="product.image.importer")
        image_importer.run(self.external_id, binding, image_record)
        return result
