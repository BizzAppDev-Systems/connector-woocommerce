import logging

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from odoo.addons.connector.exception import MappingError

# pylint: disable=W7950

_logger = logging.getLogger(__name__)


class WooProductTemplateBatchImporter(Component):
    """Batch Importer the WooCommerce Product Template"""

    _name = "woo.product.template.batch.importer"
    _inherit = "woo.delayed.batch.importer"
    _apply_on = "woo.product.template"


class WooProductTemplateImportMapper(Component):
    """Impoter Mapper for the WooCommerce Product Template"""

    _name = "woo.product.template.import.mapper"
    _inherit = "woo.import.mapper"
    _apply_on = "woo.product.template"

    @mapping
    def name(self, record):
        """Mapping for Name"""
        name = record.get("name")
        product_tmp_id = record.get("id")
        if not name:
            raise MappingError(
                _("Product Template name doesn't exist for Product ID %s Please check")
                % product_tmp_id
            )
        return {"name": name}

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


class WooProductTemplateImporter(Component):
    """Importer the WooCommerce Product Template"""

    _name = "woo.product.template.importer"
    _inherit = "woo.importer"
    _apply_on = "woo.product.template"

    def _get_attribute_id_format(self, attribute, record, option=None):
        """Return the attribute and attribute value's unique id"""
        if not option:
            return "{}-{}".format(attribute.get("name"), record.get("id"))
        return "{}-{}-{}".format(option, attribute.get("id"), record.get("id"))

    def _after_import(self, binding, **kwargs):
        """
        This method overrides the default behavior of _after_import when importing
        images from a remote record. If no image records are found in the remote record,
        it returns the result of the super class's '_after_import' method.
        """
        result = super(WooProductTemplateImporter, self)._after_import(
            binding, **kwargs
        )

        binder = self.binder_for("woo.product.attribute")
        attribute_records = []

        for woo_attribute in self.remote_record.get("attributes", []):
            woo_attribute_id = woo_attribute.get("id")
            if woo_attribute_id == 0:
                attribute_id = self._get_attribute_id_format(
                    woo_attribute, self.remote_record
                )
            else:
                attribute_id = binder.to_internal(woo_attribute_id, unwrap=True)

            value_ids = []
            if "options" in woo_attribute:
                for option in woo_attribute["options"]:
                    value = attribute_id.value_ids.filtered(lambda v: v.name == option)
                    if value:
                        value_ids.append(value.id)

            existing_attribute = binding.odoo_id.attribute_line_ids.filtered(
                lambda line: line.attribute_id.id == attribute_id.id
            )

            if existing_attribute:
                existing_attribute.write({"value_ids": [(6, 0, value_ids)]})
            else:
                if value_ids:
                    attribute_records.extend(
                        [
                            (
                                0,
                                0,
                                {
                                    "attribute_id": attribute_id.id,
                                    "value_ids": [(6, 0, value_ids)],
                                },
                            )
                        ]
                    )

        if attribute_records:
            binding.odoo_id.write({"attribute_line_ids": attribute_records})

        binding.sync_product_variants_from_woo()
        return result

    # def _import_dependencies(self):
    #     """
    #     Override method to import dependencies for WooCommerce products.
    #     It retrieves grouped products from the remote record.
    #     """
    #     record = self.remote_record.get("variations", [])
    #     for product in record:
    #         lock_name = "import({}, {}, {}, {})".format(
    #             self.backend_record._name,
    #             self.backend_record.id,
    #             "woo.product.product",
    #             product,
    #         )
    #         self.advisory_lock_or_retry(lock_name)
    #     for product in record:
    #         _logger.debug("product: %s", product)
    #         if product:
    #             self._import_dependency(product, "woo.product.product")

    #     return super(WooProductTemplateImporter, self)._import_dependencies()
