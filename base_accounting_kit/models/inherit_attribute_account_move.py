from odoo import models, fields

class InheritAccountMove(models.Model):
    _inherit = 'account.move'

    partner_id = fields.Many2one('res.partner')
    product_id = fields.Many2one('product.product')
    account_id = fields.Many2one('account.account')