from odoo import fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    donasi_id = fields.Many2one('donasi.management', string='Donasi')
