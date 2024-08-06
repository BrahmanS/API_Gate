from odoo import models, fields, api, _

class MasterGroupTags(models.Model):
    _name = "master.group.tags"
    _description = "Master Group Tags"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char('Nama Group Tags')
    code = fields.Char('Kode')
