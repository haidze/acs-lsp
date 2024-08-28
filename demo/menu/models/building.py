from odoo import models, fields


class Building(models.Model):
    _name = 'building'
    _description = 'Building'
    _table = 'res_building'

    code = fields.Char(string="Code", required=True)
    name = fields.Char(string="Name", required=True)
    note = fields.Html(string="Note")
    longitude = fields.Char(string="Longitude")
    latitude = fields.Char(string="Latitude")
    plant_id = fields.Many2one('plant', string="Plant", required=True)
    approve_by = fields.Many2one('res.users', string="Approved by", required=True)
    manager_id = fields.Many2one('res.users', string="Manager", required=True)
    sequence = fields.Integer(string="Sequence")
    gate_ids = fields.Many2many('gate', string="Gate Information")
