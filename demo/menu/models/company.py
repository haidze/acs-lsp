from odoo import models, fields


class Company(models.Model):
    _name = 'company'
    _description = 'Company'
    _table = 'sys_company'

    code = fields.Char(string="Code", required=True)
    name = fields.Char(string="Name", required=True)
    logo = fields.Char(string="Logo Path")
    email = fields.Char(string="Email")
    phone = fields.Char(string="Phone")
    address = fields.Char(string="Address")
    tax_code = fields.Char(string="Tax Code")
    website = fields.Char(string="Website")
    note = fields.Html(string="Note")
