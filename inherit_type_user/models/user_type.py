from odoo import api, fields, models, _

class UserType(models.Model):
    _inherit = 'res.users'

    tipe_user = fields.Selection([
        ('siswa', 'Siswa'),
        ('ortu', 'Ortu'),
	    ('mgm', 'Management'),
        ('gr', 'Guru'),
    ], string='Tipe User')
    # email_user = fields.Char('Email')

# class AmLine(models.Model):
#     _inherit = 'account.move.line'

#     group = fields.Many2one('master.group', string='Group')