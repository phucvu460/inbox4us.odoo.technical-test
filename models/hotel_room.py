from odoo import models, fields, api, _
from odoo.exceptions import UserError

class HotelRoom(models.Model):
    _name = 'hotel.room'
    _description = 'Hotel Room'

    name = fields.Char(string='Room Number', required=True)
    room_type = fields.Selection([
        ('single', 'Single'),
        ('double', 'Double'),
        ('suite', 'Suite'),
    ], string='Room Type', required=True)
    price_per_night = fields.Float(string='Price per Night', required=True)
    status = fields.Selection([
        ('available', 'Available'),
        ('booked', 'Booked'),
        ('maintenance', 'Maintenance'),
    ], string='Status', default='available')

    @api.constrains('status')
    def _check_room_status(self):
        today = fields.Date.today()
        for room in self:
            if room.status == 'maintenance':
                # When set a room as in maintenance, we should check if there exists any booking for this room
                active_bookings = self.env['hotel.booking'].search([
                    ('room_id', '=', room.id),
                    ('check_in_date', '<=', today),
                    ('check_out_date', '>=', today)
                ])
                if active_bookings:
                    raise UserError(_('There are active bookings for this room. Please handle these bookings first before set the room to maintenance'))

    def update_room_status(self):
        today = fields.Date.today()
        domain = [
            ('room_id', 'in', self.ids),
            ('check_in_date', '<=', today),
            ('check_out_date', '>=', today)
        ]
        bookings = self.env['hotel.booking'].read_group(domain, ['room_id'], ['room_id'])
        booked_room_ids = [booking['room_id'][0] for booking in bookings]

        for room in self:
            if room.id in booked_room_ids:
                room.write({'status': 'booked'})
            else:
                is_maintenance = room.status == 'maintenance'
                room.write({'status': 'available' if not is_maintenance else 'maintenance'})

    @api.model
    def cron_update_room_status(self):
        # This cron run daily to update room status
        rooms = self.search([])
        rooms.update_room_status()
            