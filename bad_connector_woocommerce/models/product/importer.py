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
    _inherit = "woo.import.mapper"
    _apply_on = "woo.product.product"

    @mapping
    def name(self, record):
        """Mapping for Name"""
        name = record.get("name")
        product_id = record.get("id")
        if not name:
            error_message = (
                f"Product name doesn't exist for Product ID {product_id} Please check!"
            )
            raise MappingError(error_message)
        return {"name": name}

    @mapping
    def list_price(self, record):
        """Mapping product Price"""
        return {"list_price": record.get("price")}

    @mapping
    def price(self, record):
        """Mapping for Standard Price"""
        price = record.get("price")
        return {"price": price} if price else {}

    @mapping
    def regular_price(self, record):
        """Mapping for Regular Price"""
        regular_price = record.get("regular_price")
        return {"regular_price": regular_price} if regular_price else {}

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
    def description(self, record):
        """Mapping for description"""
        description = record.get("description")
        return {"description": description} if description else {}

    @mapping
    def purchase_ok(self, record):
        """Mapping for purchase_ok"""
        return {"purchase_ok": record.get("purchasable", False)}

    @mapping
    def status(self, record):
        """Mapping for status"""
        status = record.get("status")
        return {"status": status} if status else {}

    @mapping
    def tax_status(self, record):
        """Mapping for tax_status"""
        tax_status = record.get("tax_status")
        return {"tax_status": tax_status} if tax_status else {}

    @mapping
    def stock_status(self, record):
        """Mapping for stock_status"""
        stock_status = record.get("stock_status")
        return {"stock_status": stock_status} if stock_status else {}

    @mapping
    def categ_id(self, record):
        """Mapping for Product category"""
        category_id = self.backend_record.product_categ_id.id
        binder = self.binder_for("woo.product.category")
        for category in record.get("categories", []):
            woo_binding = binder.to_internal(category.get("id"))
            if woo_binding and woo_binding.odoo_id:
                category_id = woo_binding.odoo_id.id
                break
        return {"categ_id": category_id}

    @only_create
    @mapping
    def detailed_type(self, record):
        """Mapping for detailed_type"""
        return {"detailed_type": self.backend_record.default_product_type}

    def _get_attribute_id_format(self, attribute, record, option=None):
        """Return the attribute and attribute value's unique id"""
        if not option:
            return "{}-{}".format(attribute.get("name"), record.get("id"))
        return "{}-{}-{}".format(option, attribute.get("id"), record.get("id"))

    def _get_product_attribute(self, attribute_id, record):
        """Get the product attribute that contains id as zero"""
        binder = self.binder_for("woo.product.attribute")
        created_id = self._get_attribute_id_format(attribute_id, record)
        product_attribute = binder.to_internal(created_id)
        if not product_attribute and not attribute_id.get("id"):
            product_attribute = self.env["woo.product.attribute"].create(
                {
                    "name": attribute_id.get("name"),
                    "backend_id": self.backend_record.id,
                    "external_id": created_id,
                    "not_real": True,
                }
            )
        return product_attribute

    def _create_attribute_values(self, options, product_attribute, attribute, record):
        """Create attribute value binding that doesn't contain ids"""
        binder = self.binder_for("woo.product.attribute.value")
        for option in options:
            created_id = self._get_attribute_id_format(attribute, record, option)
            product_attribute_value = binder.to_internal(created_id)
            if not product_attribute_value:
                attribute_id = self._get_attribute_id_format(attribute, record)
                binder = self.binder_for("woo.product.attribute")
                product_attr = binder.to_internal(attribute_id, unwrap=True)
                attribute_value = self.env["product.attribute.value"].search(
                    [
                        ("name", "=", option),
                        ("attribute_id", "=", product_attr.id),
                    ],
                    limit=1,
                )
                self.env["woo.product.attribute.value"].create(
                    {
                        "name": option,
                        "attribute_id": product_attribute.odoo_id.id,
                        "woo_attribute_id": product_attribute.id,
                        "backend_id": self.backend_record.id,
                        "external_id": created_id,
                        "odoo_id": attribute_value.id if attribute_value else None,
                    }
                )
        return True

    @mapping
    def woo_attribute_ids(self, record):
        """Mapping of woo_attribute_ids"""
        attribute_ids = []
        woo_product_attributes = record.get("attributes", [])
        if not woo_product_attributes:
            return {}
        binder = self.binder_for("woo.product.attribute")
        for attribute in woo_product_attributes:
            attribute_id = attribute.get("id")
            woo_binding = binder.to_internal(attribute_id)
            if woo_binding:
                attribute_ids.append(woo_binding.id)
                continue
            product_attribute = self._get_product_attribute(attribute, record)
            if "options" in attribute:
                self._create_attribute_values(
                    attribute["options"], product_attribute, attribute, record
                )
            attribute_ids.append(product_attribute.id)
        return {"woo_attribute_ids": [(6, 0, attribute_ids)]}

    @mapping
    def woo_product_categ_ids(self, record):
        """Mapping for woo_product_categ_ids"""
        category_ids = []
        woo_product_categories = record.get("categories", [])
        binder = self.binder_for("woo.product.category")
        for category in woo_product_categories:
            woo_binding = binder.to_internal(category.get("id"))
            if not woo_binding:
                continue
            category_ids.append(woo_binding.id)
        return {"woo_product_categ_ids": [(6, 0, category_ids)]} if category_ids else {}

    @mapping
    def product_tag_ids(self, record):
        """Mapping for product_tag_ids"""
        tag_ids = []
        tags = record.get("tags", [])
        binder = self.binder_for("woo.product.tag")
        for tag in tags:
            product_tag = binder.to_internal(tag.get("id"), unwrap=True)
            if not product_tag:
                continue
            tag_ids.append(product_tag.id)
        return {"product_tag_ids": [(6, 0, tag_ids)]} if tag_ids else {}

    @mapping
    def woo_product_attribute_value_ids(self, record):
        """Mapping for woo_product_attribute_value_ids"""
        attribute_value_ids = []
        woo_attributes = record.get("attributes", [])
        binder = self.binder_for("woo.product.attribute")
        for woo_attribute in woo_attributes:
            attribute_id = woo_attribute.get("id")
            if attribute_id == 0:
                attribute_id = self._get_attribute_id_format(woo_attribute, record)
            attribute = binder.to_internal(attribute_id, unwrap=True)
            options = woo_attribute.get("options", [])
            for option in options:
                attribute_value = self.env["woo.product.attribute.value"].search(
                    [
                        ("name", "=", option),
                        ("attribute_id", "=", attribute.id),
                    ],
                    limit=1,
                )
                if not attribute_value:
                    raise MappingError(
                        _("'%s' attribute value not found!Import Attribute first.")
                        % option
                    )
                attribute_value_ids.append(attribute_value.id)
        return {"woo_product_attribute_value_ids": [(6, 0, attribute_value_ids)]}

    # def get_product_template(self, temp=None):
    #     binder = self.binder_for(model="woo.product.template")
    #     template_id = binder.to_internal(temp, unwrap=True)
    #     print("\n\n template_id====", template_id)
    #     return template_id

    # @mapping
    # def product_tmpl_id(self, record):
    #     template_id = self.get_product_template(temp=record.get("parent_id"))
    #     return {"product_tmpl_id": template_id.id} if template_id else {}


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
        # print("\n\n after import record====", self.remote_record)
        product = self.remote_record
        # print("\n\n payload===", product)
        if product.get("type") == "variable":
            # print("\n\n inside variable product------")
            template_record = binding.odoo_id.product_tmpl_id
            woo_bind_ids = template_record.woo_bind_ids

            existing_record = self.env["woo.product.template"].search(
                [
                    ("backend_id", "=", self.backend_record.id),
                    ("external_id", "=", product.get("id")),
                    ("odoo_id", "=", template_record.id),
                ],
                limit=1,
            )
            # print("\n\n existing==", existing_record)
            if not existing_record:
                new_binding_record = self.env["woo.product.template"].create(
                    {
                        "backend_id": self.backend_record.id,
                        "external_id": product.get("id"),
                        "odoo_id": template_record.id,
                    }
                )
                woo_bind_ids = [(4, new_binding_record.id, False)]
                template_record.write({"woo_bind_ids": woo_bind_ids})

        image_record = self.remote_record.get("images")
        if not image_record:
            return result
        image_importer = self.component(usage="product.image.importer")
        image_importer.run(self.external_id, binding, image_record)

        return result

    def _import_dependencies(self):
        """
        Override method to import dependencies for WooCommerce product.
        """
        record = self.remote_record
        for line in record.get("variations", []):
            lock_name = "import({}, {}, {}, {})".format(
                self.backend_record._name,
                self.backend_record.id,
                "woo.product.product",
                line,
            )
            self.advisory_lock_or_retry(lock_name)

        for line in record.get("variations", []):
            _logger.debug("line: %s", line)
            self._import_dependency(line, "woo.product.product")

        return super(WooProductProductImporter, self)._import_dependencies()
