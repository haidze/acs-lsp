from odoo import http
from odoo.http import request
import json

class ComingPlanController(http.Controller):

    @http.route('/coming_plan/notifications', type='http', auth='user', csrf=False)
    def get_notifications(self):
        # Lấy các thông báo liên quan đến 'coming.plan'
        notifications = request.env['mail.message'].search([
            ('model', '=', 'coming.plan')
        ], order='id desc', limit=10)

        result = []
        for notification in notifications:
            result.append({
                'title': notification.subject,
                'message': notification.body,
                'timestamp': notification.create_date.strftime('%Y-%m-%d %H:%M:%S'),
            })

        # Trả về kết quả dưới dạng JSON
        return request.make_response(json.dumps({'notifications': result}),
                                     headers=[('Content-Type', 'application/json')])
