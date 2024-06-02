import json
from datetime import datetime

from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

from ..utils.jwt_provider import JWTProvider
from ..utils.request_validator import RequestValidator


class BookingController(http.Controller):

    @http.route('/api/bookings', type='json', auth='public', methods=['POST'])
    @RequestValidator.validate_request(RequestValidator.booking_schema())
    @JWTProvider.jwt_required
    def create_booking(self):
        # TODO: need to handle authentication access token
        # TODO: Implement booking creation logic
        # Note: need to check availability of the room
        post_data = json.loads(request.httprequest.data)        

        customer_id = post_data['customer_id']
        room_id = post_data['room_id']
        check_in_date = datetime.strptime(post_data['checkin_date'], DEFAULT_SERVER_DATE_FORMAT)
        check_out_date = datetime.strptime(post_data['checkout_date'], DEFAULT_SERVER_DATE_FORMAT)

        try:
            # Call the create_booking method in the model
            booking = request.env['hotel.booking'].create_booking(customer_id, room_id, check_in_date, check_out_date)
            return {'success': True, 'booking_id': booking.id}
        except ValidationError as e:
            request.env.cr.rollback()
            return {'success': False, 'error': str(e)}        
