from odoo import models, fields

class AcsRegisterBuildingLines(models.Model):
    _name = 'acs.register.building.lines'
    _description = 'Register Building Lines'

    building_id = fields.Many2one('res.building', string='Working Area', required=True)
    register_id = fields.Many2one('visitor.registration', string='Register', required=True)


class ResBuilding(models.Model):
    _name = 'res.building'
    _description = 'Working Areas Information'

    code = fields.Char(string='Working Area Code', required=True)
    name = fields.Char(string='Working Area Name', required=True)
    note = fields.Text(string='Note')
    longitude = fields.Char(string='Longitude')
    latitude = fields.Char(string='Latitude')
    plant_id = fields.Many2one('res.plants', string='Plant')
    approve_by = fields.Many2one('res.users', string='Approved By')
    manager_id = fields.Many2one('res.users', string='Manager')
    sequence = fields.Integer(string='Sequence')


class ResPlants(models.Model):
    _name = 'res.plants'
    _description = 'Plant Information'

    code = fields.Char(string='Plant Code', required=True)
    name = fields.Char(string='Plant Name', required=True)
    note = fields.Text(string='Note')
    company_id = fields.Many2one('sys.company', string='Company', required=True)
    address = fields.Char(string='Address')
    phone = fields.Char(string='Phone Number')
    email = fields.Char(string='Email')

