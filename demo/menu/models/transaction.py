from odoo import models, fields, api
import logging
import json

_logger = logging.getLogger(__name__)

class Transaction(models.Model):
    _name = 'transaction'
    _description = 'Transaction'
    _table = 'acs_transaction'

    id = fields.Char(string="ID", required=True, copy=False, readonly=True, index=True,
                     default=lambda self: self.env['ir.sequence'].next_by_code('acs.transaction'))
    transaction_id_in = fields.Char(string="Transaction ID In")
    register_id = fields.Many2one('acs.register', string="Register")
    register_code = fields.Char(string="Register Code")
    coming_plan_id = fields.Many2one('coming.plan', string="Coming Plan")
    gate_id = fields.Many2one('gate', string="Gate In")
    lane_id = fields.Many2one('lane', string="Lane In")
    transaction_date = fields.Datetime(string="Transaction Date In")
    plate_system = fields.Char(string="Plate System In")
    plate_input = fields.Char(string="Plate Input In")
    plate_other = fields.Char(string="Plate Other In")
    vehicle_image = fields.Char(string="Vehicle Image In")
    plate_image = fields.Char(string="Plate Image In")
    reason_id = fields.Many2one('res.reason', string="Reason In")
    reason_string = fields.Char(string="Reason String In")
    security_submit_id = fields.Char(string="Security Submit ID In")
    submit_date = fields.Datetime(string="Submit Date In")
    weigh_kgs_in = fields.Char(string="Weigh (kgs) In")
    transaction_id_out = fields.Char(string="Transaction ID Out")
    gate_id_out = fields.Many2one('res.gate', string="Gate Out")
    lane_id_out = fields.Many2one('res.lane', string="Lane Out")
    transaction_date_out = fields.Datetime(string="Transaction Date Out")
    plate_system_out = fields.Char(string="Plate System Out")
    plate_input_out = fields.Char(string="Plate Input Out")
    plate_other_out = fields.Char(string="Plate Other Out")
    vehicle_image_out = fields.Char(string="Vehicle Image Out")
    plate_image_out = fields.Char(string="Plate Image Out")
    reason_id_out = fields.Many2one('res.reason', string="Reason Out")
    security_submit_id_out = fields.Char(string="Security Submit ID Out")
    submit_date_out = fields.Datetime(string="Submit Date Out")
    reason_string_out = fields.Char(string="Reason String Out")
    status = fields.Selection([('1', 'Check in'), ('2', 'Check out')], string="Status")
    weigh_kgs_out = fields.Char(string="Weigh (kgs) Out")
    transaction_type_id = fields.Many2one('res.transaction.type', string="Transaction Type")

    pre_registered_visitors = fields.Integer(string="Pre-Registered Visitors", compute='_compute_dashboard_data')
    signed_in_visitors = fields.Integer(string="Signed-In Visitors", compute='_compute_dashboard_data')
    signed_out_visitors = fields.Integer(string="Signed-Out Visitors", compute='_compute_dashboard_data')
    cancelled_appointments = fields.Integer(string="Cancelled Appointments", compute='_compute_dashboard_data')
    purpose_of_visit_data = fields.Text(string="Purpose of Visit Data", compute='_compute_dashboard_data')
    working_areas_data = fields.Text(string="Working Areas Data", compute='_compute_dashboard_data')

    @api.depends('status', 'transaction_id_in')
    def _compute_dashboard_data(self):
        for record in self:
            record.pre_registered_visitors = self.search_count([('transaction_id_in', '!=', False)])
            record.signed_in_visitors = self.search_count([('status', '=', '1')])
            record.signed_out_visitors = self.search_count([('status', '=', '2')])
            record.cancelled_appointments = self.env['coming.plan'].search_count(
                [('vehicle_status', '=', 'Rejected')])
            record.waiting_for_approval = self.env['acs.register'].search_count(
                [('state', '=', 'waiting_for_approval')])

            purpose_count = {}
            registers = self.env['acs.register'].search([])
            for register in registers:
                for purpose in register.purpose_of_visit:
                    if purpose.name in purpose_count:
                        purpose_count[purpose.name] += 1
                    else:
                        purpose_count[purpose.name] = 1
            record.purpose_of_visit_data = json.dumps(purpose_count)

            # Tính toán cho working_areas
            areas_count = {}
            for register in registers:
                for area in register.required_working_areas:
                    if area.name in areas_count:
                        areas_count[area.name] += 1
                    else:
                        areas_count[area.name] = 1
            record.working_areas_data = json.dumps(areas_count)

    def get_dashboard_data(self):
        # Phương thức này sẽ trả về dữ liệu cho dashboard
        purpose_count = {}
        working_area_count = {}

        registers = self.env['acs.register'].search([])
        for register in registers:
            for purpose in register.purpose_of_visit:
                if purpose.name in purpose_count:
                    purpose_count[purpose.name] += 1
                else:
                    purpose_count[purpose.name] = 1

            for area in register.required_working_areas:
                if area.name in working_area_count:
                    working_area_count[area.name] += 1
                else:
                    working_area_count[area.name] = 1

        data = {
            'pre_registered_visitors': self.search_count([('transaction_id_in', '!=', False)]),
            'signed_in_visitors': self.search_count([('status', '=', '1')]),
            'signed_out_visitors': self.search_count([('status', '=', '2')]),
            'cancelled_appointments': self.env['coming.plan'].search_count([('vehicle_status', '=', 'Rejected')]),
            'waiting_for_approval': self.env['acs.register'].search_count([('state', '=', 'waiting_for_approval')]),
            'purpose_of_visit_data': json.dumps(purpose_count),
            'working_areas_data': json.dumps(working_area_count),
        }

        _logger.info('Dashboard Data: %s', data)

        return data
