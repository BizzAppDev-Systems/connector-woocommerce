"""

Exporters for woo.

In addition to its export job, an exporter has to:

* check in woo if the record has been updated more recently than the
  last sync date and if yes, delay an import
* call the ``bind`` method of the binder to update the last sync date

"""

import logging

from odoo.addons.component.core import AbstractComponent

_logger = logging.getLogger(__name__)


class WooExporter(AbstractComponent):
    """A common flow for the exports to woocommerce"""

    _name = "woo.exporter"
    _inherit = ["base.generic.exporter", "connector.woo.base"]
    _usage = "record.exporter"
    _default_binding_field = "woo_bind_ids"
    _skip_should_import = False

    def _should_import(self, **kwargs):
        """
        Inherited method that determines whether to import updated data at remote
        level.This functionality is skipped during the time of sale order export.
        """
        if self._skip_should_import:
            return
        return super(WooExporter, self)._should_import(**kwargs)


class WooBatchExporter(AbstractComponent):
    """
    The role of a BatchExporter is to search for a list of
    items to export, then it can either export them directly or delay
    the export of each item separately.
    """

    _name = "woo.batch.exporter"
    _inherit = ["generic.batch.exporter", "connector.woo.base"]
    _usage = "batch.exporter"


class WooDirectBatchExporter(AbstractComponent):
    """Export the records directly, without delaying the jobs."""

    _name = "woo.direct.batch.exporter"
    _inherit = ["generic.direct.batch.exporter", "connector.woo.base"]


class WooDelayedBatchExporter(AbstractComponent):
    """Delay export of the records"""

    _name = "woo.delayed.batch.exporter"
    _inherit = ["generic.delayed.batch.exporter", "connector.woo.base"]
