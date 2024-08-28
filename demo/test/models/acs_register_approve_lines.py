from odoo import models, fields

class AcsRegisterApproveLines(models.Model):
    _name = 'acs.register.approve.lines'
    _description = 'Register Approve Lines'

    register_id = fields.Many2one('visitor.registration', string='Register', required=True)
    approver_id = fields.Many2one('res.users', string='Approver', required=True)
    approve_date = fields.Date(string='Approve Date')
    status = fields.Selection([
        ('0', 'Waiting'),
        ('1', 'Approved'),
        ('2', 'Reject')
    ], string='Status', default='0')
    sequence = fields.Integer(string='Sequence')
    reason = fields.Char(string='Reason')
