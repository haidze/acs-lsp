from odoo import http, fields, _
from odoo.http import request, Response
import json
import logging

_logger = logging.getLogger(__name__)

class ControlInOutLogController(http.Controller):

    @http.route('/control_in_out/all', type='http', auth='public', methods=['GET'], csrf=False)
    def get_all_logs(self):
        logs = request.env['control.in.out'].search([])
        result = []
        for log in logs:
            transaction_type_display = dict(request.env['coming.plan']._fields['transaction_type_id'].selection).get(
                log.coming_plan_id.transaction_type_id, "Unknown")

            log_data = {
                'reg_no': log.coming_plan_id.register_code,
                'plate': log.vehicle_plate_number,
                'driver_name': log.coming_plan_id.driver_name,
                'vehicle_type': transaction_type_display,
                'start_date': log.coming_plan_id.access_start_date.strftime('%m/%d/%Y') if log.coming_plan_id.access_start_date else '',
                'start_time': f"{int(log.coming_plan_id.access_start_time)}:{int((log.coming_plan_id.access_start_time - int(log.coming_plan_id.access_start_time)) * 60)}",
                'end_date': log.coming_plan_id.access_end_date.strftime('%m/%d/%Y') if log.coming_plan_id.access_end_date else '',
                'end_time': f"{int(log.coming_plan_id.access_end_time)}:{int((log.coming_plan_id.access_end_time - int(log.coming_plan_id.access_end_time)) * 60)}",
                'status': log.coming_plan_id.coming_plan_status,
                'register_id': log.register_id.id if log.register_id else None,
                'reason': log.reason_label if log.reason_label else '',
            }
            result.append(log_data)

        return Response(json.dumps(result), content_type='application/json', status=200)

    @http.route('/control_in_out/get_register_info', type='http', auth='user')
    def get_register_info(self, register_id):
        # Tìm kiếm log với register_id cụ thể
        log = request.env['control.in.out'].search([('register_id', '=', int(register_id))], limit=1)

        if not log:
            return Response(json.dumps({'error': 'No logs found for this Register ID'}),
                            content_type='application/json', status=404)
        data = {
            'register_id': log.register_id.id,
            'reg_no': log.register_id.reg_no,
            'vehicle_plate': log.vehicle_plate_number,
            'register_date': log.register_id.register_date.strftime('%m/%d/%Y'),
            'host': log.register_id.register_user.name if log.register_id.register_user else None,
            'driver_name': log.register_id.visitor_name,
            'driver_id': log.register_id.visitor_id,
            'start_date': log.register_id.start_date.strftime('%m/%d/%Y'),
            'end_date': log.register_id.end_date.strftime('%m/%d/%Y'),
            'start_time': f"{int(log.register_id.start_time)}:{int((log.register_id.start_time - int(log.register_id.start_time)) * 60)}",
            'end_time': f"{int(log.register_id.end_time)}:{int((log.register_id.end_time - int(log.register_id.end_time)) * 60)}",
            'required_working_areas': [area.name for area in log.register_id.required_working_areas],
            'gates': [gate.name for gate in log.register_id.gates],
            'vehicle_status': log.status_label,
            'reg_status': log.register_id.state,
        }

        return Response(json.dumps([data]), content_type='application/json', status=200)

    @http.route('/control_in_out/update_status', type='http', auth='user', methods=['POST'], csrf=False)
    def update_status(self, **kwargs):
        try:
            register_id = kwargs.get('register_id')
            status = kwargs.get('status')

            if not register_id or not status:
                return Response(json.dumps({'success': False, 'error': 'Missing parameters'}),
                                content_type='application/json', status=400)

            # Tìm đối tượng log với register_id
            log = request.env['control.in.out'].search([('register_id', '=', int(register_id))], limit=1)
            if log:
                # Cập nhật trạng thái mới
                log.write({'status': status})

                # Thêm user hiện tại vào làm follower để nhận thông báo email
                log.message_subscribe(partner_ids=[request.env.user.partner_id.id])

                # Tạo một activity để thông báo cho người dùng
                activity = request.env['mail.activity'].create({
                    'activity_type_id': request.env.ref('mail.mail_activity_data_email').id,
                    'summary': 'Status Updated',
                    'note': f'The status for vehicle {log.vehicle_plate_number} has been updated to {log.status_label}.',
                    'res_model_id': request.env['ir.model']._get('control.in.out').id,
                    'res_id': log.id,
                    'user_id': request.env.user.id,
                })

                log.activity_ids = [(4, activity.id)]

                return Response(json.dumps({'success': True}), content_type='application/json', status=200)
            else:
                return Response(json.dumps({'success': False, 'error': 'Log not found'}),
                                content_type='application/json', status=404)
        except Exception as e:
            _logger.exception("Error updating status")
            return Response(json.dumps({'success': False, 'error': str(e)}), content_type='application/json',
                            status=500)