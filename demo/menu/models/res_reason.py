from odoo import models, fields, api

class ResReason(models.Model):
    _name = 'res.reason'
    _description = 'Approve & Reject Reasons'

    code = fields.Char(string="Code", required=True)
    name = fields.Char(string="Name", required=True)
    note = fields.Text(string="Note")
    type = fields.Selection([
        ('1', 'Approve reasons'),
        ('2', 'Reject reasons'),
    ], string="Reason Type", required=True)


