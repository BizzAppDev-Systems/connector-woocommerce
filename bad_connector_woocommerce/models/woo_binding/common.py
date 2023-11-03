from odoo import fields, models

# from odoo.addons.component.core import Component


class WooBinding(models.AbstractModel):
    """Abstract Model for the Bindings."""

    _name = "woo.binding"
    _inherit = "base.binding"
    _description = "WooCommerce Binding (abstract)"

    backend_id = fields.Many2one(
        comodel_name="woo.backend",
        string="Backend",
        required=True,
        ondelete="restrict",
    )

    def init(self):
        """
        Inherit Method: inherit method to add unique index for odoo connector
        """
        if self._table == "woo_binding":
            return
        return super().init()

    woo_data = fields.Text()
