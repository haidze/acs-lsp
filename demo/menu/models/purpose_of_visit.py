from odoo import models, fields

class ResPurposeOfVisit(models.Model):
    _name = 'purpose.of.visit'
    _description = 'Purpose of Visit'
    _table = 'res_purpose_of_visit'

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Name', required=True)
    note = fields.Html(string="Note")
    type = fields.Selection([
        ('request', 'Request'),
        ('other', 'Other')
    ], string='Type', default='request', required=True)
