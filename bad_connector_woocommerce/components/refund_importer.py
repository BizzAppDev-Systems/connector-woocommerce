import logging

# from datetime import datetime

# from odoo import _, fields

from odoo.addons.component.core import AbstractComponent

# from odoo.addons.connector.exception import IDMissingInBackend
# from odoo.addons.queue_job.exception import NothingToDoJob
# from odoo.addons.queue_job.job import identity_exact

_logger = logging.getLogger(__name__)


class WooRefundImporter(AbstractComponent):
    """Base importer for woocommerce"""

    _name = "woo.refund.importer"
    _inherit = ["base.importer", "connector.woo.base"]
    _usage = "record.refund.importer"


class WooRefundBatchImporter(AbstractComponent):
    """Base refund batch importer for woocommerce"""

    _name = "woo.refund.batch.importer"
    _inherit = ["woo.batch.importer"]
    _usage = "record.batch.refund.importer"
