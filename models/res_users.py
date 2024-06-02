from odoo import models, api, _
from odoo.exceptions import AccessDenied


class ResUser(models.AbstractModel):
    _inherit = "res.users"

    @api.model
    def register_user(self, vals):
        public_user_template = self.env.ref('base.public_user')
        new_user = public_user_template.sudo().copy(vals)
        new_user.sudo().write({'password': vals.get('password')})
        return new_user

    @api.model
    def verify_login(self, login, password):
        user = self.env['res.users'].sudo().search([('login', '=', login)], limit=1)
        return user if self._check_password(user, password) else False

    def _check_password(self, user, password):
        # Validate user password. This function is inspired by _check_credentials() from base Odoo
        self.env.cr.execute(
            "SELECT COALESCE(password, '') FROM res_users WHERE id=%s",
            [user.id]
        )
        [hashed] = self.env.cr.fetchone()
        valid, replacement = self._crypt_context()\
            .verify_and_update(password, hashed)
        if replacement is not None:
            self._set_encrypted_password(self.env.user.id, replacement)
        if not valid:
            raise AccessDenied()
        return True
