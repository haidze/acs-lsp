from odoo import http
from odoo.http import request
import json

class DashboardController(http.Controller):

    @http.route('/dashboard', type='http', auth='user', website=True)
    def dashboard_view(self, **kwargs):
        Transaction = request.env['transaction']
        dashboard_data = Transaction.get_dashboard_data()

        return request.render('menu.dashboard_template', {
            'pre_registered_visitors': dashboard_data['pre_registered_visitors'],
            'signed_in_visitors': dashboard_data['signed_in_visitors'],
            'signed_out_visitors': dashboard_data['signed_out_visitors'],
            'cancelled_appointments': dashboard_data['cancelled_appointments'],
            'waiting_for_approval': dashboard_data['waiting_for_approval'],
            'purpose_of_visit_data': dashboard_data['purpose_of_visit_data'],
            'working_areas_data': dashboard_data['working_areas_data'],
        })
