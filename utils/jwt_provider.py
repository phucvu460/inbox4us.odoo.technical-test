import jwt
import datetime
from functools import wraps

from odoo.http import request

SECRET_KEY = "secret key"

class JWTProvider:
    @staticmethod
    def encode_token(user_id):
        """Generates the JWT token"""
        token_payload = {
            'user_id': user_id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Token expires in 1 hour
        }
        token = jwt.encode(token_payload, SECRET_KEY, algorithm='HS256')
        return token

    @staticmethod
    def decode_token(token):
        """Decodes the JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return {'error': 'Token has expired'}
        except jwt.InvalidTokenError:
            return {'error': 'Invalid token'}
        
    @staticmethod
    def jwt_required(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = request.httprequest.headers.get('Authorization')
            if not token:
                return {
                    'status': 403,
                    'error': 'Token is missing'
                }
            try:
                token = token.split(" ")[1]
                payload = JWTProvider.decode_token(token)
                if 'error' in payload:
                    return {
                        'status': 403,
                        'error': payload['error']
                    }
                if 'user_id' not in payload:
                    return {
                        'status': 403,
                        'error': 'Token is invalid'
                    }
            except Exception as e:
                return {
                    'status': 403,
                    'error': str(e)
                }
            return f(*args, **kwargs)
        
        return wrapper