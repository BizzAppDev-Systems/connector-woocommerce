from odoo import _, models


class QueueJob(models.Model):
    _inherit = "queue.job"

    def open_related_action(self):
        """Used to open related record of queue job"""
        self.ensure_one()
        if not self.args and not self.kwargs:
            return None
        if self.args:
            if not len(self.args) > 1:
                return None
            if isinstance(self.args[1], str) or isinstance(self.args[1], int):
                external_id = self.args[1]
                record = self.env[self.model_name].search(
                    [("external_id", "=", external_id)]
                )
                if hasattr(self.env[self.model_name], "odoo_id"):
                    record = record.odoo_id
            else:
                record = self.args[1]
        elif self.kwargs:
            external_id = self.kwargs.get("external_id")
            if not external_id:
                return None
            if external_id:
                record = (
                    self.env[self.model_name]
                    .search([("external_id", "=", external_id)])
                    .odoo_id
                )
        action = {
            "name": _("Related Record"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": record._name,
        }
        if len(record) == 1:
            action["res_id"] = record.id
        else:
            action.update(
                {
                    "name": _("Related Records"),
                    "view_mode": "tree,form",
                    "domain": [("id", "in", record.ids)],
                }
            )
        return action
