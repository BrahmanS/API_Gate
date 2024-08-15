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
        
    @http.route('/api/wakaf/<int:donasi_id>', auth='public', methods=['GET'], type='http', csrf=False)
    def get_donasi_id(self, donasi_id):
        try:
            # Fetch the Donasi Management record
            record = request.env['wakaf.management'].sudo().browse(donasi_id)
            if not record.exists():
                return self._json_response({'status': 404, 'message': 'Donasi not found'})

            # Fetch RAB Donasi Line records
            rab_lines = record.rab_wakaf_ids
            rab_wakaf_data = []
            for rab in rab_lines:
                if rab.product_id and hasattr(rab.product_id, 'name'):
                    rab_data = {
                        'id': rab.id,
                        'product_id': rab.product_id.id,
                        'name': rab.product_id.name,
                        'nilai_paket': rab.nilai,
                        'total_paket': rab.total,
                    }
                    rab_wakaf_data.append(rab_data)
                else:
                    # Log atau tangani kasus di mana product_id tidak ada atau tidak memiliki atribut name
                    print(f"Warning: Product for RAB ID {rab.id} is missing or does not have a name attribute")

            # # Fetch Register Donasi Donatur records
            # donatur_lines = record.donatur_donasi_ids
            # donatur_donasi_data = []
            # for donatur in donatur_lines:
            #     donatur_data = {
            #         'id': donatur.id,
            #         'product_id': donatur.product_id.id,
            #         'product_name': donatur.product_id.name,
            #         'donatur_id': donatur.donatur_id.id,
            #         'donatur_name': donatur.donatur_id.nama_donatur,
            #         'email': donatur.email,
            #         'phone': donatur.phone,
            #         'infaq_date': donatur.infaq_date.strftime('%Y-%m-%d') if donatur.infaq_date else '',
            #         'nilai_donasi': donatur.nilai_donasi,
            #         'total_donasi': donatur.total_donasi,
            #         'note': donatur.note,
            #         'partner_id': donatur.partner_id.id,
            #         'qty': donatur.qty,
            #     }
            #     donatur_donasi_data.append(donatur_data)

            # Compile Donasi Management data
            donasi_data = {
                    'id': record.id,
                    'nama_program': record.nama_program,
                    # 'name': record.product_id.name,
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
                    'rab_wakaf_data': rab_wakaf_data,
                    'keterangan': record.keterangan,

            }

            return self._json_response({'status': 200, 'response': donasi_data, 'message': 'Success'})

        except Exception as e:
            _logger.error(f"Error fetching donasi data: {str(e)}")
            return self._json_response({'status': 500, 'message': f'Error: {str(e)}'})


    def _json_response(self, data):
        return request.make_response(
            data=json.dumps(data),
            headers={'Content-Type': 'application/json'}
        )
