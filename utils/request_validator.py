from schema import Schema, And, Regex, Use
from schema import SchemaError

from functools import wraps
import json
from datetime import datetime

from odoo.http import request
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class RequestValidator: 
    @staticmethod
    def auth_register_schema():
        return Schema({
            'email': And(str, Regex(r'^\S+@\S+\.\S+$')),
            'name': str,
            'password': And(str, len)
        })
    
    @staticmethod
    def auth_login_schema():
        return Schema({
            'email': And(str, Regex(r'^\S+@\S+\.\S+$')),
            'password': And(str, len)
        })
    
    @staticmethod
    def booking_schema():
        return Schema({
            'room_id': int,
            'customer_id': int,
            'checkin_date': Use(lambda v: datetime.strptime(v, DEFAULT_SERVER_DATE_FORMAT)),    # Add date validation if needed
            'checkout_date': Use(lambda v: datetime.strptime(v, DEFAULT_SERVER_DATE_FORMAT)),   # Add date validation if needed
        })
    
    @staticmethod
    def validate_request(schema):
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                try:
                    post_data = json.loads(request.httprequest.data)
                    schema.validate(post_data)
                except SchemaError as e:
                    return {
                        'status': 400,
                        'error': str(e)
                    }
                except json.JSONDecodeError:
                    return {
                        'status': 400,
                        'error': 'Invalid JSON format'
                    }
                return f(*args, **kwargs)
            return wrapper
        return decorator
    

