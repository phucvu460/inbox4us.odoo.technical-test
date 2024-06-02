import json

from odoo import http, _
from odoo.http import request
from odoo.addons.auth_signup.models.res_users import SignupError

from ..utils.jwt_provider import JWTProvider
from ..utils.request_validator import RequestValidator

SECRET_KEY = 'your_secret_key_here'


class AuthController(http.Controller):

    @http.route('/api/register', type='json', auth="none", methods=['POST'], cors='*', csrf=False)
    @RequestValidator.validate_request(RequestValidator.auth_register_schema())
    def register(self):
        # TODO: Implement user registration logic
        post_data = json.loads(request.httprequest.data) 
        try:
            self._signup_user(post_data)
            return {'success': _('User created successfully')}
        except SignupError as e:
            return {'error': str(e)}
    
    @http.route('/api/login', type='json', auth='none', methods=['POST'], cors='*', csrf=False)
    @RequestValidator.validate_request(RequestValidator.auth_login_schema())
    def login(self):
        # TODO: Implement user login logic and return JWT token
        post_data = json.loads(request.httprequest.data)        
        login = post_data['email']
        password = post_data['password']
        user = request.env['res.users'].verify_login(login, password)
        if not user:
            return {'error': _('Invalid email or password')}
        
        # Generate JWT token
        token = JWTProvider.encode_token(user.id)
        return {'token': token}
        
    def _prepare_register_user_values(self, post_data):
        return {
            'active': True,
            'login': post_data['email'],
            'email': post_data['email'],
            'name': post_data['name'],
            'password': post_data['password']
        }

    def _signup_user(self, post_data):
        if request.env['res.users'].sudo().search([('login', '=', post_data['email'])], limit=1):
            raise SignupError(_('Another user is already registered using this email address.'))

        values = self._prepare_register_user_values(post_data)
        return request.env['res.users'].register_user(values)