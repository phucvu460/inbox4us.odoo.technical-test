from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HotelBooking(models.Model):
    _name = 'hotel.booking'
    _description = 'Hotel Booking'

    customer_id = fields.Many2one('hotel.customer', string='Customer', required=True)
    room_id = fields.Many2one('hotel.room', string='Room', required=True)
    check_in_date = fields.Date(string='Check-in Date', required=True)
    check_out_date = fields.Date(string='Check-out Date', required=True)
    total_amount = fields.Float(string='Total Amount', compute='_compute_total_amount', store=True)

    @api.depends('room_id', 'check_in_date', 'check_out_date')
    def _compute_total_amount(self):
        for booking in self:
            if booking.check_in_date and booking.check_out_date:
                num_nights = (booking.check_out_date - booking.check_in_date).days
                booking.total_amount = booking.room_id.price_per_night * num_nights
    
    @api.constrains('check_in_date', 'check_out_date')
    def _check_date(self):
        for booking in self:
            if booking.check_in_date < fields.Date.today():
                raise ValidationError(_('Check-in date cannot be in the past.'))
            if booking.check_in_date > booking.check_out_date:
                raise ValidationError(_('Check-in date must precede check-out date.'))

    @api.constrains('room_id', 'check_in_date', 'check_out_date')
    def _check_room_availability(self):
        for booking in self:
            # Check if room status is not available
            if booking.room_id.status == 'maintenance':
                raise ValidationError(_('The room is currently in maintenance'))

            # Check if there are any overlapping bookings
            overlapping_bookings = self.env['hotel.booking'].search([
                ('room_id', '=', booking.room_id.id),
                ('check_in_date', '<', booking.check_out_date),
                ('check_out_date', '>', booking.check_in_date),
                ('id', '!=', booking.id)
            ])
            if overlapping_bookings:
                raise ValidationError(_('The room is already booked for the selected dates.'))
    
    @api.model
    def create_booking(self, customer_id, room_id, check_in_date, check_out_date):
        # Create the booking
        booking = self.sudo().create([{
            'customer_id': customer_id,
            'room_id': room_id,
            'check_in_date': check_in_date,
            'check_out_date': check_out_date,
        }])
        return booking

    @api.model_create_multi
    def create(self, vals_list):
        bookings = super().create(vals_list)
        for booking in bookings:
            # Try update room status instantly, in case the customer check in today and the cron already run 
            booking.room_id.update_room_status()
        return bookings

    def write(self, vals):
        res = super(HotelBooking, self).write(vals)
        if any(key in vals for key in ['room_id', 'check_in_date', 'check_out_date']):      
            for booking in self:
                booking.room_id.update_room_status()
        return res

    def unlink(self):
        rooms = self.mapped('room_id')
        res = super(HotelBooking, self).unlink()
        for room in rooms:
            room.update_room_status()
        return res
