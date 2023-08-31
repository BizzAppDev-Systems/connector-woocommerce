import logging

from odoo import _, tools
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from odoo.exceptions import ValidationError
from odoo.addons.connector.exception import IDMissingInBackend

_logger = logging.getLogger(__name__)


class WooSaleOrderExporterMapper(Component):
    _name = "woo.sale.order.export.mapper"
    _inherit = "woo.export.mapper"
    _apply_on = "woo.sale.order"

    @mapping
    def status(self, record):
        """Mapping for Status"""
        return (
            {"status": "completed"}
            if record.picking_ids.state == "done"
            and self.backend_record.mark_completed
            else {}
        )

    @mapping
    def tracking_number(self, record):
        """Mapping for tracking number"""
        tracking_number = False
        pickings = record.picking_ids.filtered(
            lambda picking: picking.state == "done" and picking.carrier_tracking_ref
        )
        if not (
            pickings
            and self.backend_record.mark_completed
            and self.backend_record.tracking_info
        ):
            return {}
        tracking_number = pickings[0].carrier_tracking_ref
        return {
            "meta_data": [
                {
                    "key": "_wc_shipment_tracking_items",
                    "value": [
                        {
                            "tracking_number": tracking_number,
                        }
                    ],
                }
            ]
        }


class WooSaleOrderBatchExporter(Component):
    _name = "woo.sale.order.batch.exporter"
    _inherit = "woo.exporter"
    _apply_on = ["woo.sale.order"]

    def run(self, binding, record=None, *args, **kwargs):
        """Run the synchronization"""
        if not binding:
            if not record:
                raise ValidationError(_("No record found to Export!!!"))
            binding = self.create_get_binding(record)
        self.binding = binding
        self.external_id = self.binder.to_external(self.binding)
        try:
            should_import = self._should_import()
        except IDMissingInBackend:
            self.external_id = None
            should_import = False
        if should_import:
            self._delay_import()
            return

        result = self._run(*args, **kwargs)
        if not self.external_id or self.external_id == "False":
            self.external_id = record.id
        self.binder.bind(self.external_id, self.binding)
        # Commit so we keep the external ID when there are several
        # exports (due to dependencies) and one of them fails.
        # The commit will also release the lock acquired on the binding
        # record
        if not tools.config["test_enable"]:
            self.env.cr.commit()  # pylint: disable=E8102
        self._after_export(binding)
        return result

    def _after_export(self, binding):
        """Import the transaction lines after checking shopify order status."""
        binding.write({"woo_order_status": "completed"})
