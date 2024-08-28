from odoo import models, fields

class ResRegisterVehicleType(models.Model):
    _name = 'register.vehicle.type'
    _description = 'Register Vehicle Type'
    _table = 'res_register_vehicle_type'

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Name', required=True)
    note = fields.Html(string='Note')
