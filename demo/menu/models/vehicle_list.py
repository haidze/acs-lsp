from odoo import models, fields, api
import base64
import io
import qrcode
import logging

_logger = logging.getLogger(__name__)

class VehicleInfo(models.Model):
    _name = 'vehicle.list'
    _description = 'Vehicle List'
    _table = 'acs_register_vehicle_lines'

    register_id = fields.Many2one('acs.register', string='Register ID', required=True, ondelete='cascade')
    code = fields.Binary(string='QR Code', compute='_generate_qr_code', store=True)
    vehicle_plate_number = fields.Char('Vehicle Plate', required=True)
    driver_name = fields.Char('Driver Name', required=True)
    driver_identity_card = fields.Char('Driver ID', required=True)
    vehicle_info = fields.Char('Vehicle Type', required=True)
    start_time = fields.Float('Start Time', digits=(6, 2))
    end_time = fields.Float('End Time', digits=(6, 2))

    @api.depends('vehicle_plate_number', 'vehicle_info')
    def _generate_qr_code(self):
        for vehicle in self:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            data = f"Vehicle Plate: {vehicle.vehicle_plate_number}\nVehicle Type: {vehicle.vehicle_info}"
            qr.add_data(data)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            vehicle.code = base64.b64encode(buffer.getvalue())
            _logger.info(f"Generated QR Code for Vehicle ID {vehicle.id}: {vehicle.code}")