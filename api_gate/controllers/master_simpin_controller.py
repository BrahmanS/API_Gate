from odoo import http, fields
from odoo.http import request, Response
from odoo.exceptions import AccessError
import json

class MasterSimpinController(http.Controller):
    @http.route('/api/master_general', type='http', auth='public', methods=['GET'], csrf=False)
    def get_master_general_data(self):
        try:
            agama_records = request.env['master.general'].sudo().search([('type_umum', '=', 'agama')])
            agama_data = [{'id': rec.id, 'name': rec.name} for rec in agama_records]

            gender_records = request.env['master.general'].sudo().search([('type_umum', '=', 'gender')])
            gender_data = [{'id': rec.id, 'name': rec.name} for rec in gender_records]

            marital_records = request.env['master.general'].sudo().search([('type_umum', '=', 'marital')])
            marital_data = [{'id': rec.id, 'name': rec.name} for rec in marital_records]

            peruntukan_records = request.env['master.general'].sudo().search([('type_umum', '=', 'peruntukan')])
            peruntukan_data = [{'id': rec.id, 'name': rec.name} for rec in peruntukan_records]

            response = {
                'status': 'success',
                'agama': agama_data,
                'gender': gender_data,
                'marital': marital_data,
                'peruntukan':peruntukan_data,
            }

            return request.make_response(json.dumps(response), headers=[('Content-Type', 'application/json')])

        except Exception as e:
            return request.make_response(json.dumps({'status': 'error', 'message': str(e)}), headers=[('Content-Type', 'application/json')])