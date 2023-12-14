import logging

from odoo import _

from odoo.addons.component.core import Component

# pylint: disable=W7950

_logger = logging.getLogger(__name__)


class WooProductProductMrpImporter(Component):
    """Importer the WooCommerce Product"""

    _inherit = "woo.product.product.importer"

    def _after_import(self, binding, **kwargs):
        """
        This method is Inherits the default behavior of _after_import when importing
        grouped type products and creating it's BoM.
        """
        result = super(WooProductProductMrpImporter, self)._after_import(
            binding, **kwargs
        )

        if self.remote_record.get("type") == "grouped":
            self.env["mrp.bom"].make_bom(binding, env=self)

        return result

    def _must_skip(self):
        """Inherited Method :: to Skip Product Records which have type as variable."""
        if self.remote_record.get("type") == "variable":
            return _(
                "Skipped: Product Type is Variable for Product ID %s"
            ) % self.remote_record.get("id")
        return super(WooProductProductMrpImporter, self)._must_skip()

    def _import_dependencies(self):
        """
        Inherited method :: to import dependencies for WooCommerce products.
        It retrieves grouped products from the remote record.
        """
        record = self.remote_record.get("grouped_products", [])
        for product in record:
            lock_name = "import({}, {}, {}, {})".format(
                self.backend_record._name,
                self.backend_record.id,
                "woo.product.product",
                product,
            )
            self.advisory_lock_or_retry(lock_name)
        for product in record:
            _logger.debug("product: %s", product)
            if product:
                self._import_dependency(product, "woo.product.product")

        return super(WooProductProductMrpImporter, self)._import_dependencies()
