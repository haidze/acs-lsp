from odoo import models, fields


class Plant(models.Model):
    _name = 'plant'
    _description = 'Plant'
    _table = 'res_plants'

    code = fields.Char(string="Code", required=True)
    name = fields.Char(string="Name", required=True)
    note = fields.Html(string="Note")
    company = fields.Char(string="Company")
    address = fields.Char(string="Address")
    phone = fields.Char(string="Phone")
    email = fields.Char(string="Email")

