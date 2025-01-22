from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from odoo.addons.connector.exception import MappingError


class ProductCommonExportMapper(Component):
    _name = "woo.product.common.export.mapper"
    _inherit = "woo.export.mapper"

    @mapping
    def sku(self, record):
        """Mapping for SKU"""
        if not record.default_code:
            raise MappingError(_("Please set the Product SKU of '%s'" % record.name))
        return {"sku": str(record.default_code) or ""}

    @mapping
    def description(self, record):
        """Mapping for description"""
        return {"description": record.description or ""}

    @mapping
    def purchasable(self, record):
        """Mapping for purchase"""
        return {"purchase": record.purchase_ok or False}

    @mapping
    def manage_stock(self, record):
        """Mapping for manage_stock"""
        return {"manage_stock": record.manage_stock_in_woocommerce}

    @mapping
    def tags(self, record):
        """Mapping for tags"""
        tags = []
        if not record.product_tag_ids:
            return {"tags": tags}
        for tag in record.product_tag_ids:
            tags.append({"id": tag.woo_bind_ids[0].external_id})
        return {"tags": tags}

    @mapping
    def categories(self, record):
        """Mapping for categories"""
        categories = []
        if not record.categ_id:
            return {"categories": categories}
        woo_category = self.env["woo.product.category"].search(
            [("odoo_id", "=", record.categ_id.id)], limit=1
        )
        if not woo_category:
            raise MappingError(
                _(
                    "Please set category %s in the related WooCommerce Category",
                    record.categ_id.name,
                )
            )
        if woo_category and woo_category.external_id:
            categories.append({"id": woo_category.external_id})
        return {"categories": categories}
