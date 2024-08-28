from odoo import models, fields


class Lane(models.Model):
    _name = 'lane'
    _description = 'Lane'
    _table = 'res_lane'

    code = fields.Char(string="Code", required=True)
    name = fields.Char(string="Name", required=True)
    gate_id = fields.Many2one('gate', string="Gate", required=True)
    note = fields.Html(string="Note")
    direction = fields.Selection([('in', 'IN'), ('out', 'OUT')], string="Direction", required=True)
    type = fields.Selection([('ACS', 'ACS'), ('LXP-STM', 'LXP-STM')], string="Type", required=True)