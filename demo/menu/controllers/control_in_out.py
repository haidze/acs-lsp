from odoo import http
from odoo.http import request

class CustomController(http.Controller):

    @http.route('/ACSControlInOut', type='http', auth='user', website=True)
    def control_in_out(self, **kwargs):
        return request.render('menu.control_in_out_template')