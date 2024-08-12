from odoo import fields, models

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    donasi_id = fields.Many2one('donasi.management', string='Donasi')
