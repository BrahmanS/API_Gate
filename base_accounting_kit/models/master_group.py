from odoo import models, fields, api, _

class MasterGroup(models.Model):
    _name = "master.group"
    _description = "Master Group"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char('Nama Group')
    code = fields.Char('Kode')