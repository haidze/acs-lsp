from odoo import models, fields

class AcsRegisterGateLines(models.Model):
    _name = 'acs.register.gate.lines'
    _description = 'Register Gate Lines'

    gate_id = fields.Many2one('res.gate', string='Gate', required=True)
    register_id = fields.Many2one('visitor.registration', string='Register', required=True)


class ResGate(models.Model):
    _name = 'res.gate'
    _description = 'Gate Information'

    code = fields.Char(string='Gate Code', required=True)
    name = fields.Char(string='Gate Name', required=True)
    note = fields.Text(string='Note')
    company_id = fields.Many2one('sys.company', string='Company', required=True)