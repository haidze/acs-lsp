from odoo import models, fields

class ResTransactionType(models.Model):
    _name = 'res.transaction.type'
    _description = 'Transaction Type'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    note = fields.Text(string="Note")