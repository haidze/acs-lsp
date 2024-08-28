from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class ComingPlan(models.Model):
    _name = 'coming.plan'
    _description = 'Coming Plan'
    _table = 'acs_coming_plan'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    id = fields.Char(string='ID', required=True)
    register_id = fields.Many2one('acs.register', string='Register ID')
    register_code = fields.Char(string='Register Code')
    access_pass_number = fields.Char(string='Access Pass Number')
    vehicle_plate_number = fields.Char(string='Vehicle Plate Number')
    vehicle_status = fields.Selection([
        ('0', 'Waiting for check'),
        ('1', 'Checked'),
        ('2', 'Rejected')
    ], string='Vehicle Status', default='0')
    process_type = fields.Selection([
        ('0', 'Manual check'),
        ('1', 'Auto process')
    ], string='Process Type', default='0')
    access_start_date = fields.Date(string='Access Start Date')
    access_end_date = fields.Date(string='Access End Date')
    access_start_time = fields.Float(string='Access Start Time')
    access_end_time = fields.Float(string='Access End Time')
    extend_end_time = fields.Float(string='Extend End Time', help='Default is Access end time')
    transaction_type_id = fields.Selection([
        ('Logistics', 'Logistic'),
        ('Whitelist', 'Whitelist'),
        ('Maintenance', 'Maintenance'),
        ('Visitor', 'Visitor')
    ], string='Transaction Type')
    logistic_order_type = fields.Char(string='Logistic Order Type')
    driver_name = fields.Char(string='Driver Name')
    driver_identity_card = fields.Char(string='Driver Identity Card')
    driver_email = fields.Char(string='Driver Email')
    driver_phone = fields.Char(string='Driver Phone')
    last_checked_in_by = fields.Char(string='Last Checked In By')
    last_checked_in_date = fields.Datetime(string='Last Checked In Date')
    last_checked_out_by = fields.Char(string='Last Checked Out By')
    last_checked_out_date = fields.Datetime(string='Last Checked Out Date')
    last_entry_date = fields.Datetime(string='Last Entry Date')
    last_exit_date = fields.Datetime(string='Last Exit Date')
    working_areas = fields.Many2many('building', string='Working Areas')
    gates = fields.Many2many('gate', string='Gates')
    last_transaction_id = fields.Char(string='Last Transaction ID')
    coming_plan_status = fields.Selection([
        ('0', 'Not approve yet'),
        ('1', 'Coming'),
        ('2', 'Entered'),
        ('3', 'Exited')
    ], string='Coming Plan Status', default='0')
    access_time = fields.Char(string='Access Time', compute='_compute_access_time')

    @api.depends('access_start_time', 'access_end_time')
    def _compute_access_time(self):
        for record in self:
            start_time = record.access_start_time or 0
            end_time = record.access_end_time or 0
            record.access_time = f"{start_time:.2f} - {end_time:.2f}"

    @api.model
    def action_checked(self):
        return True

    @api.model
    def action_rejected(self):
        return True

    @api.model
    def action_terminated(self):
        return True

    @api.model
    def action_close(self):
        return True

    def _create_notification(self, action_type):
        gates_names = ', '.join(self.gates.mapped('name'))
        message = (
            f"[VISUAL - CHECK]<br/>"
            f"VISUAL CHECK THE VEHICLE -<br/>"
            f"PLEASE CHECK VEHICLE PLATE: {self.vehicle_plate_number or 'Unknown'} -<br/>"
            f"GATE: {gates_names or 'Unknown'}<br/><br/>"
            f"<a href='/web#id={self.id}&model=coming.plan&view_type=form' target='_blank'>Click here for details!</a>"
        )

        # Tìm đối tác (partner) tương ứng với tài xế dựa trên email của tài xế
        driver_partner = self.env['res.partner'].search([('email', '=', self.driver_email)], limit=1)

        if not driver_partner:
            raise ValueError(f"Không tìm thấy tài xế với email {self.driver_email}")

        # Tạo một thông báo (notification)
        notification = self.env['mail.message'].create({
            'body': message,
            'subject': f"[ACCESS IN - OUT] Notification\n",
            'message_type': 'notification',
            'subtype_id': self.env.ref('mail.mt_comment').id,
            'model': self._name,
            'res_id': self.id,
            'author_id': self.env.user.partner_id.id,  # Người gửi là người dùng hiện tại
        })

        # Tạo một activity để hiển thị trên giao diện web của Odoo với người nhận là tài xế
        self.activity_schedule(
            'mail.mail_activity_data_todo',
            summary=f"Coming Plan {action_type.capitalize()}",
            note=message,
            user_id=driver_partner.user_ids[0].id if driver_partner.user_ids else None,
            date_deadline=fields.Date.context_today(self),
            activity_type_id=self.env.ref('mail.mail_activity_data_todo').id,
        )

    @api.model
    def create(self, vals):
        record = super(ComingPlan, self).create(vals)
        record._create_notification('created')
        return record

    def write(self, vals):
        result = super(ComingPlan, self).write(vals)
        self._create_notification('updated')
        return result