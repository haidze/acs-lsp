from odoo import models, fields, api,exceptions
import base64
import logging

_logger = logging.getLogger(__name__)

class PersonInfo(models.Model):
    _name = 'person.list'
    _description = 'Person List'
    _table = 'acs_register_material_lines'

    register_id = fields.Many2one('acs.register', string='Register ID', required=True, ondelete='cascade')
    person_name = fields.Char('Full Name')
    person_identity_card = fields.Char('Vietnamese ID')
    person_picture = fields.Binary('Person Picture')
    person_company = fields.Char('Company Name')
    person_phone = fields.Char('Phone')
    person_email = fields.Char('Email')
    vehicle_plate_number = fields.Char('Vehicle Plate')

