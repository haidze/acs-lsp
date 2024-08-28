from odoo import models, fields

class VisitorRegistration(models.Model):
    _name = 'visitor.registration'
    _description = 'Visitor Registration'

    register_code = fields.Char(string='Register Code', required=True, unique=True)
    register_name = fields.Char(string='Description')
    visitor_name = fields.Char(string='Visitor Name')
    visitor_identity_card = fields.Char(string='Identity Card')
    visitor_phone_number = fields.Char(string='Visitor phone')
    visitor_email = fields.Char(string='Email')
    visitor_job_position = fields.Char(string='Job Position')
    visitor_company = fields.Char(string='Company')
    visitor_applied_date = fields.Date(string='Applied Date')

    # Foreign Key Fields
    register_visitor_type_id = fields.Many2one('res.register.visitor.type', string='Register type')
    transaction_type_id = fields.Many2one('res.transaction.type', string='Transaction type')
    company_id = fields.Many2one('sys.company', string='Company', invisible=True)
    request_user_id = fields.Many2one('res.users', string='Requester')

    purpose_of_visit_id = fields.Char(string='Purpose')
    request_date = fields.Datetime(string='Request Date')
    job_position = fields.Char(string='Job Position')
    department_id = fields.Many2one('sys.department', string='Department')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    note = fields.Text(string='Note')
    status = fields.Selection([
        ('0', 'Preparing'),
        ('1', 'Waiting for approval'),
        ('2', 'Rejected'),
        ('3', 'Terminated'),
        ('4', 'Approved')
    ], string='Status', default='0')
    reject_reason = fields.Char(string='Reject Reason')
    is_accepted_terms = fields.Boolean(string='Accepted terms')
    is_truck_scale = fields.Boolean(string='Use truck scale')

class ResRegisterVisitorType(models.Model):
    _name = 'res.register.visitor.type'
    _description = 'Register Visitor Type'

    code = fields.Char(string='Code', required=True, unique=True)
    name = fields.Char(string='Name', required=True)
    note = fields.Text(string='Note')

class ResTransactionType(models.Model):
    _name = 'res.transaction.type'
    _description = 'Transaction Type'

    code = fields.Char(string='Code', required=True, unique=True)
    name = fields.Char(string='Name', required=True)
    note = fields.Text(string='Note')

class SysCompany(models.Model):
    _name = 'sys.company'
    _description = 'Company'

    code = fields.Char(string='Company Code', required=True, unique=True)
    name = fields.Char(string='Company Name', required=True)
    logo = fields.Char(string='Logo Path')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone Number')
    address = fields.Char(string='Address')
    taxcode = fields.Char(string='Tax Code')
    website = fields.Char(string='Website')
    note = fields.Text(string='Note')

class SysDepartment(models.Model):
    _name = 'sys.department'
    _description = 'Department'

    code = fields.Char(string='Code', required=True, unique=True)
    name = fields.Char(string='Name', required=True)
    note = fields.Text(string='Note')
