import logging

from odoo.addons.component.core import Component

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

    # @mapping
    # def name(self, record):
    #     """Mapping for Name"""
    #     name = record.get("name")
    #     product_id = record.get("id")
    #     if not name:
    #         error_message = (
    #             f"Product name doesn't exist for Product ID
    # {product_id} Please check!"
    #         )
    #         raise MappingError(error_message)
    #     return {"name": name}

    # @mapping
    # def default_code(self, record):
    #     """Mapped product default code."""
    #     default_code = record.get("sku")
    #     if not default_code and not self.backend_record.without_sku:
    #         raise MappingError(
    #             _("SKU is Missing for the product '%s' !", record.get("name"))
    #         )
    #     return {"default_code": default_code} if default_code else {}

    # @mapping
    # def description(self, record):
    #     """Mapping for description"""
    #     description = record.get("description")
    #     return {"description": description} if description else {}

    # @mapping
    # def product_variant_ids(self, record):
    #     """Mapping of product variant"""
    #     variant_ids = []
    #     binder = self.binder_for("woo.product.product")
    #     for variant in record.get("variations", []):
    #         product_variant = binder.to_internal(variant, unwrap=True)
    #         if not product_variant:
    #             continue
    #         variant_ids.append(product_variant.id)
    #     return {"product_variant_ids": [(6, 0, variant_ids)]} if variant_ids else {}


class WooProductTemplateImporter(Component):
    """Importer the WooCommerce Product Template"""

    _name = "woo.product.template.importer"
    _inherit = "woo.importer"
    _apply_on = "woo.product.template"

    # def _after_import(self, binding, **kwargs):
    #     """
    #     This method is Overrides the default behavior of _after_import.
    #     """
    #     result = super(WooProductTemplateImporter, self)._after_import(
    #         binding, **kwargs
    #     )
    #     variant_ids = []
    #     binder = self.binder_for("woo.product.product")
    #     for variant in self.remote_record.get("variations", []):
    #         product_variant = binder.to_internal(variant, unwrap=True)
    #         if not product_variant:
    #             continue
    #         variant_ids.append(product_variant.id)
    #     binding.write({"product_variant_ids": [(6, 0, variant_ids)]})
    #     return result

    # def _must_skip(self):
    #     """Skipped Records which have type as variable."""
    #     if self.remote_record.get("type") != "variable":
    #         return _("Skipped: Product Type is not Variable")
    #     return super(WooProductTemplateImporter, self)._must_skip()

    # def _import_dependencies(self):
    #     """
    #     Override method to import dependencies for WooCommerce.
    #     """
    #     record = self.remote_record
    #     for line in record.get("variations", []):
    #         lock_name = "import({}, {}, {}, {})".format(
    #             self.backend_record._name,
    #             self.backend_record.id,
    #             "woo.product.product",
    #             line,
    #         )
    #         self.advisory_lock_or_retry(lock_name)

    #     for line in record.get("variations", []):
    #         _logger.debug("line: %s", line)
    #         self._import_dependency(line, "woo.product.product")

    #     return super(WooProductTemplateImporter, self)._import_dependencies()
