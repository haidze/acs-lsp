from odoo import models, fields

class Department(models.Model):
    _name = 'job.position'
    _description = 'Job Position'
    _table = 'res_job_position'

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Name', required=True)
    note = fields.Html(string="Note")
