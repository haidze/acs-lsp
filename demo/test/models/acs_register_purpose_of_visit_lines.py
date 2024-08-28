from odoo import models, fields

class RegisterPurposeOfVisitLines(models.Model):
    _name = 'acs.register.purpose.of.visit.lines'
    _description = 'Register Purpose Of Visit Lines'

    purpose_id = fields.Many2one('res.register.vehicle.type', string='Purpose', required=True)
    register_id = fields.Many2one('visitor.registration', string='Register', required=True)

class ResRegisterVehicleType(models.Model):
    _name = 'res.register.vehicle.type'
    _description = 'Register Vehicle Type'

    code = fields.Char(string='Code', required=True, unique=True)
    name = fields.Char(string='Name', required=True)
    note = fields.Text(string='Note')
