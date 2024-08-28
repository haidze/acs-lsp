from odoo import models, fields

class Department(models.Model):
    _name = 'department'
    _description = 'Department'
    _table = 'sys_department'

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Name', required=True)
    note = fields.Html(string="Note")
