import base64
import json
from lxml import etree
from odoo import models, fields, api, exceptions, _
import logging
from datetime import datetime
_logger = logging.getLogger(__name__)

class AcsRegister(models.Model):
    _name = 'acs.register'
    _description = 'ACS Register'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    reg_no = fields.Char(string='Reg. No', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    register_user = fields.Many2one('res.users', string='Register User', default=lambda self: self.env.user)
    job_position = fields.Char(string='Job Position', required=True)
    vehicle_type_id = fields.Many2one('register.vehicle.type', string='Vehicle Type', default=lambda self: self._get_default_vehicle_type(), readonly=True)
    register_date = fields.Date(string='Register Date', default=fields.Date.today)
    department = fields.Char(string='Department', required=True)
    visitor_name = fields.Char(string='Visitor Name', required=True)
    visitor_id = fields.Char(string='Visitor ID', required=True)
    email = fields.Char(string='Email', required=True)
    phone = fields.Char(string='Phone', required=True)
    company = fields.Char(string='Company', required=True)
    date_applied = fields.Date(string='Date Applied', default=fields.Date.today)
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    start_time = fields.Float(string="Start Time")
    end_time = fields.Float(string="End Time")
    register_type = fields.Selection([('individual', 'Individual'), ('group', 'Group')], string="Register Type")
    purpose_of_visit = fields.Many2many('purpose.of.visit', string='Purpose of Visit', required=True)
    required_working_areas = fields.Many2many('building', string='Required Working Areas', required=True)
    gates = fields.Many2many('gate', string='Gates', required=True)
    note = fields.Html(string="Note")
    state = fields.Selection([
        ('preparing', 'Preparing'),
        ('waiting_for_approval', 'Waiting for Approval'),
        ('rejected', 'Rejected'),
        ('terminated', 'Terminated'),
        ('approved', 'Approved'),
    ], string='State', readonly=True, copy=False, index=True, tracking=3, default='preparing')
    approver_ids = fields.One2many('acs.register.approver', 'entry_id', string='Approvers')
    log_ids = fields.One2many('acs.register.log', 'entry_id', string='Logs')
    message_ids = fields.One2many('mail.message', 'res_id', domain=lambda self: [('model', '=', self._name)],
                                  string='Messages', readonly=True)
    activity_ids = fields.One2many('mail.activity', 'res_id', domain=lambda self: [('res_model', '=', self._name)],
                                   string='Activities', readonly=True)
    vehicle_ids = fields.One2many('vehicle.list', 'register_id', string='Vehicles')
    person_ids = fields.One2many('person.list', 'register_id', string='Persons')
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments', help='Attachments related to this entry')

    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(AcsRegister, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            doc = etree.XML(res['arch'])
            readonly_fields = self._get_readonly_fields()
            for node in doc.xpath("//field"):
                if node.get('name') in readonly_fields:
                    modifiers = json.loads(node.get("modifiers") or "{}")
                    if self.state == 'waiting_for_approval':
                        modifiers['readonly'] = True
                    else:
                        modifiers.pop('readonly', None)
                    node.set("modifiers", json.dumps(modifiers))
            res['arch'] = etree.tostring(doc, encoding='unicode')
        return res

    def _get_readonly_fields(self):
        return [
            'reg_no', 'register_user', 'job_position', 'vehicle_type', 'register_date',
            'department', 'visitor_name', 'visitor_id', 'email', 'phone', 'company',
            'date_applied', 'start_date', 'end_date', 'start_time', 'end_time',
             'register_type','purpose_of_visit', 'required_working_areas', 'gates', 'note'
        ]

    @api.model
    def _get_default_vehicle_type(self):
        vehicle_type_id = self.env.context.get('default_vehicle_type_id')
        if vehicle_type_id:
            vehicle_type = self.env['register.vehicle.type'].search([('id', '=', vehicle_type_id)], limit=1)
            if vehicle_type:
                return vehicle_type.id
        return self.env['register.vehicle.type'].search([], limit=1).id

    @api.model
    def create(self, vals):
        if vals.get('reg_no', _('New')) == _('New'):
            vals['reg_no'] = self.env['ir.sequence'].next_by_code('acs.register') or _('New')
        entry = super(AcsRegister, self).create(vals)
        entry.send_email_and_notification('waiting_for_approval')
        entry.create_log('ACS Register created')
        return entry

    def write(self, vals):
        if 'state' in vals and vals['state'] == 'rejected':
            for entry in self:
                entry.approver_ids.write({'status': 'rejected'})

        if self.state == 'waiting_for_approval' and any(field in vals for field in self._get_readonly_fields()):
            raise exceptions.UserError('You cannot modify this record when it is waiting for approval.')

        return super(AcsRegister, self).write(vals)

    def get_user_email(self):
        user_email = self.env.user.email
        if not user_email or '@' not in user_email:
            user_email = 'no-reply@example.com'
        return user_email

    def get_register_user_email(self):
        if self.register_user and self.register_user.email:
            return self.register_user.email
        return 'no-reply@example.com'

    def create_pdf_report(self):
        try:
            report_template = self.env.ref('menu.action_report_acs_register')
            pdf_content = self.env['ir.actions.report']._render_qweb_pdf(report_template, [self.id])
            return pdf_content
        except Exception as e:
            _logger.error("Error creating PDF report: %s", e)
            raise

    def send_email_and_notification(self, state, email_to=None, recipient_name=None):
        try:
            template_ref = 'menu.email_template_%s' % state
            _logger.info("Fetching email template with ref: %s", template_ref)
            template = self.env.ref(template_ref)
            if not template:
                raise exceptions.UserError('Email template not found.')

            # Generate PDF report
            pdf_content = self.create_pdf_report()

            # Create attachment
            attachment = self.env['ir.attachment'].create({
                'name': 'ACS_Register_Report.pdf',
                'type': 'binary',
                'datas': base64.b64encode(pdf_content[0]),
                'res_model': self._name,
                'res_id': self.id,
                'mimetype': 'application/pdf'
            })
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            user_email = self.get_user_email()
            email_values = {
                'email_from': user_email,
                'email_to': email_to,
                'attachment_ids': [(4, attachment.id)],
            }

            # Ensure recipient_name is a string
            if not recipient_name:
                recipient_name = "Recipient"

            ctx = {
                'recipient_name': recipient_name,
                'current_time': current_time
            }

            template.with_context(ctx).send_mail(self.id, email_values=email_values, force_send=True)

            # Send browser notification to the same user
            if email_to:
                recipient_user = self.env['res.users'].search([('email', '=', email_to)], limit=1)
                if recipient_user:
                    notification_body = f"The ACS register '{self.reg_no}' has been {state.replace('_', ' ')}."
                    self.activity_schedule(
                        'mail.mail_activity_data_todo',
                        user_id=recipient_user.id,
                        note=notification_body,
                        summary=state.replace('_', ' ').capitalize(),
                        activity_type_id=self.env.ref('mail.mail_activity_data_todo').id,
                        date_deadline=fields.Date.today()
                    )
        except Exception as e:
            _logger.error("Error sending email and notification: %s", e)
            raise

    def action_submit_for_approval(self):
        self.write({'state': 'waiting_for_approval'})
        first_approver = self.approver_ids.filtered(lambda a: a.sequence == 1 and a.status == 'waiting')
        if first_approver:
            _logger.info("Found first approver: %s", first_approver.approver_id.name)
            if first_approver.approver_id.email:
                self.send_email_and_notification('waiting_for_approval', email_to=first_approver.approver_id.email,
                                                 recipient_name=first_approver.approver_id.name)
                self.create_log('Submitted for approval to %s' % first_approver.approver_id.name)
            else:
                _logger.warning("Approver %s has no valid email.", first_approver.approver_id.name)
        else:
            _logger.warning("No approvers found or all approvers already processed.")

    def send_security_email(self, vehicle, coming_plan):
        try:
            # Kiểm tra trạng thái trước khi gửi email
            if self.state != 'approved':
                _logger.info(f"Skipping security email sending since state is {self.state}")
                return

            # Tìm kiếm mẫu email theo ID hoặc tham chiếu
            template = self.env.ref('menu.email_template_security_notification')
            if not template:
                raise exceptions.UserError('Email template not found.')

            # Lấy thông tin email người gửi và người nhận
            email_from = self.get_register_user_email()
            email_to = 'haidepmamay4@gmail.com'

            # Gửi email
            template.send_mail(coming_plan.id, email_values={'email_from': email_from, 'email_to': email_to},
                               force_send=True)

            _logger.info(f"Security email sent for coming plan {coming_plan.id}")

        except Exception as e:
            _logger.error(f"Error sending security email: {e}")
            raise exceptions.UserError(f"Error sending security email: {e}")

    def action_approve(self):
        for entry in self:
            if not entry.is_user_approver():
                raise exceptions.AccessError("You do not have the necessary permissions to approve this entry.")

            approver_entry = entry.approver_ids.filtered(
                lambda a: a.approver_id.id == entry.env.user.id and a.status == 'waiting')
            if approver_entry:
                approver_entry.ensure_one()
                approver_entry.write({'status': 'approved'})
                next_approver_entry = entry.approver_ids.filtered(
                    lambda a: a.sequence == approver_entry.sequence + 1 and a.status == 'waiting')
                if next_approver_entry:
                    next_approver_entry.ensure_one()
                    entry.send_email_and_notification('waiting_for_approval',
                                                      email_to=next_approver_entry.approver_id.email,
                                                      recipient_name=next_approver_entry.approver_id.name)
                    entry.create_log('Submitted for approval to %s' % next_approver_entry.approver_id.name)
                else:
                    entry.write({'state': 'approved'})
                    email_approved = [(self.get_register_user_email(), self.register_user.name),
                                      (self.email, self.visitor_name)]
                    for email, name in email_approved:
                        entry.send_email_and_notification('approved', email_to=email, recipient_name=name)
                    entry.create_log('Approved and notification sent to final recipient: %s' % email_approved)
                    entry.write({'state': 'approved'})

                    if entry.state == 'approved':
                        for vehicle in entry.vehicle_ids:
                            coming_plan = self.env['coming.plan'].create({
                                'register_id': entry.id,
                                'register_code': entry.reg_no,
                                'access_pass_number': entry.reg_no,
                                'vehicle_plate_number': vehicle.vehicle_plate_number,
                                'access_start_date': entry.start_date,
                                'access_end_date': entry.end_date,
                                'access_start_time': entry.start_time,
                                'access_end_time': entry.end_time,
                                'transaction_type_id': entry.vehicle_type_id.name,
                                'driver_name': entry.visitor_name,
                                'driver_identity_card': entry.visitor_id,
                                'driver_email': entry.email,
                                'driver_phone': entry.phone,
                                'coming_plan_status': '1',
                                'working_areas': [(6, 0, entry.required_working_areas.ids)],
                                'gates': [(6, 0, entry.gates.ids)],
                            })
                            _logger.info(f"Vehicle details for security email: {vehicle.vehicle_plate_number}, "
                                         f"Driver Name: {vehicle.driver_name}")
                            entry.send_security_email(vehicle, coming_plan)
            else:
                raise exceptions.AccessError("You have already approved or are not in the list of approvers.")


    def action_reject(self, reason=None):
        if not self.is_user_approver():
            raise exceptions.AccessError("You do not have the necessary permissions to reject this entry.")
        self.write({'state': 'rejected'})
        self.approver_ids.write({'status': 'rejected'})
        email_to = self.get_register_user_email()
        self.send_email_and_notification('rejected', email_to=email_to)
        if reason:
            self.create_log('Rejected: %s' % reason)
        else:
            self.create_log('Rejected')

    def action_open_reject_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'reject.reason.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('menu.view_reject_reason_wizard_form').id,
            'target': 'new',
            'context': {
                'default_entry_id': self.id,
            },
        }

    def action_terminate(self):
        self.write({'state': 'terminated'})
        email_recipients = [(self.get_register_user_email(), self.register_user.name), (self.email, self.visitor_name)]
        for email, name in email_recipients:
            self.send_email_and_notification('terminated', email_to=email, recipient_name=name)
        self.create_log('Terminated')

    def create_log(self, activity):
        self.env['acs.register.log'].create({
            'entry_id': self.id,
            'activity': activity,
            'date': fields.Datetime.now(),
        })

    def is_user_approver(self):
        self.ensure_one()
        return self.env.user.id in self.approver_ids.mapped('approver_id').ids

    def get_record_link(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        record_link = f"{base_url}/web#id={self.id}&model={self._name}&view_type=form&menu_id="
        _logger.info("Generated record link: %s", record_link)
        return record_link

    def name_get(self):
        result = []
        for record in self:
            name = record.reg_no
            result.append((record.id, name))
        return result


class AcsRegisterApprover(models.Model):
    _name = 'acs.register.approver'
    _description = 'ACS Register Approver'

    entry_id = fields.Many2one('acs.register', string='ACS Register', required=True, ondelete='cascade')
    sequence = fields.Integer(string='Sequence', default=1)
    approver_id = fields.Many2one('res.users', string='Approver', required=True)
    status = fields.Selection([
        ('waiting', 'Waiting'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='waiting', string='Status')

class AcsRegisterLog(models.Model):
    _name = 'acs.register.log'
    _description = 'ACS Register Log'

    entry_id = fields.Many2one('acs.register', string='ACS Register', required=True, ondelete='cascade')
    activity = fields.Char(string='Activity', required=True)
    date = fields.Datetime(string='Date', default=fields.Datetime.now)