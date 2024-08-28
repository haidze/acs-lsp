from odoo import models, fields

class Gate(models.Model):
    _name = 'gate'
    _description = 'Gate'
    _table = 'res_gate'

    code = fields.Char(string="Code", required=True)
    name = fields.Char(string="Name", required=True)
    note = fields.Text(string="Note")
    company = fields.Char(string="Company")