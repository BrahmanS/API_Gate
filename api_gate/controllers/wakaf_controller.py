from odoo import http, fields
from odoo.http import request, Response
import json
import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class DonationController(http.Controller):

    @http.route('/api/wakaf', auth='public', methods=['GET'], type='http', csrf=False)
    def get_wakaf(self, **kwargs):
        try:
            wakaf_records = request.env['wakaf.management'].sudo().search([])
            wakaf_list = []

            for record in wakaf_records:
                wakaf_list.append({
                    'id': record.id,
                    'nama_program': record.nama_program,
                    'program_wakaf_id': record.program_wakaf_id.id,
                    'category_wakaf_id': record.category_wakaf_id.id,
                    'tipe_wakaf_id': record.tipe_wakaf_id,
                    'keterangan': record.keterangan,
                    'saldo': record.saldo,
                    'tersalurkan': record.tersalurkan,
                    'date_begin': record.date_begin.strftime('%Y-%m-%d') if record.date_begin else '',
                    'date_end': record.date_end.strftime('%Y-%m-%d') if record.date_end else '',
                    'yayasan': record.yayasan_id.name,
                    'person_id': record.person_id.id,
                    'target_terkumpul': record.target_terkumpul,
                    'progres_saldo_terkumpul': record.progres_saldo_terkumpul,
                    
                    'keterangan': record.keterangan,
                })

            return request.make_response(
                data=json.dumps({'status': 200, 'message': 'Success', 'data': wakaf_list}),
                headers={'Content-Type': 'application/json'}
            )
        except Exception as e:
            return request.make_response(
                data=json.dumps({'status': 500, 'message': 'Error: %s' % str(e)}),
                headers={'Content-Type': 'application/json'}
            )