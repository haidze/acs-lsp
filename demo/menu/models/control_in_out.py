from odoo import models, fields, api

class ActivityLog(models.Model):
    _name = 'control.in.out'
    _description = 'Control In Out'
    _table = 'acs_control_in_out'
    _inherit = ['mail.thread']

    id = fields.Char(string='ID', required=True)
    vehicle_plate_number = fields.Char(string='Vehicle Plate Number', required=True)
    record_date = fields.Datetime(string='Record Date', default=fields.Datetime.now)
    gate_id = fields.Many2one('gate', string='Gate ID')
    lane_id = fields.Many2one('lane', string='Lane ID')
    message_en = fields.Char(string='Message EN', size=100)
    message_vn = fields.Char(string='Message VN', size=100)

    status = fields.Selection([
        ('0', 'Check'),
        ('1', 'Done')
    ], string='Status', default='0')

    register_id = fields.Many2one(related='coming_plan_id.register_id', string='Register ID', store=True)

    reason = fields.Selection([
        ('0', 'Error: Cannot get data'),
        ('1', 'Success'),
        ('10', 'Visual Check'),
        ('11', 'Not yet registered'),
        ('12', 'Invalid Access time'),
        ('13', 'Blacklist'),
        ('14', 'Not yet approve the register'),
        ('15', 'Not found transaction in'),
        ('16', 'Wrong gate')
    ], string='Reason')

    coming_plan_id = fields.Many2one('coming.plan', string='Coming Plan ID')

    status_label = fields.Char(string='Status Label', compute='_compute_status_label')
    reason_label = fields.Char(string='Reason Label', compute='_compute_reason_label')
    activity_ids = fields.One2many('mail.activity', 'res_id', string='Activities',domain=[('res_model', '=', 'control.in.out')])

    @api.depends('status')
    def _compute_status_label(self):
        status_dict = dict(self._fields['status'].selection)
        for record in self:
            record.status_label = status_dict.get(record.status, '')

    @api.depends('reason')
    def _compute_reason_label(self):
        reason_dict = dict(self._fields['reason'].selection)
        for record in self:
            record.reason_label = reason_dict.get(record.reason, '')

