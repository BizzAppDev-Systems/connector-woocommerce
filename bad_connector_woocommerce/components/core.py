from odoo.addons.component.core import AbstractComponent


class ConnectorWooBaseComponent(AbstractComponent):
    """
    Base woocommerce Connector Component
    All components of this connector should inherit from it.
    """

    _name = "connector.woo.base"
    _inherit = "base.generic.connector"
    _collection = "woo.backend"

    # def generate_lock(self, model, external_id, export=True, **kwargs):
    #     """Generic Method to apply lock for the dependencies"""
    #     lock_name = "{}({}, {}, {}, {})".format(
    #         "export" if export else "import",
    #         self.backend_record._name,
    #         self.backend_record.id,
    #         model,
    #         external_id,
    #     )
    #     # Keep a lock on this import until the transaction is committed
    #     # The lock is kept since we have detected that the informations
    #     # will be updated into Odoo
    #     self.advisory_lock_or_retry(lock_name)
