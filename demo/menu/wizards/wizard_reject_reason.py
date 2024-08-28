from odoo import models, fields, api

class RejectReasonWizard(models.TransientModel):
    _name = 'reject.reason.wizard'
    _description = 'Reject Reason Wizard'

    reason = fields.Text(string='Reason', required=True)
    entry_id = fields.Many2one('acs.register', string='ACS Register', required=True)

    def action_confirm(self):
        self.ensure_one()
        self.entry_id.action_reject(reason=self.reason)
        return {'type': 'ir.actions.act_window_close'}
