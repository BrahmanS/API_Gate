from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    tipe_donatur_id = fields.Many2one('master.tipe.donatur', string='Tipe Donatur')
