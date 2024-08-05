from odoo import http
from odoo.http import request, Response
import json
import logging

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
                    'yayasan_id': record.yayasan_id.id,
                    'person_id': record.person_id.id,
                    'target_terkumpul': record.target_terkumpul,
                    'progres_saldo_terkumpul': record.progres_saldo_terkumpul,
                    'jumlah_donatur_wakaf': record.jumlah_donatur_wakaf,
                    'product_id': record.product_id.id,
                    'qty': record.qty,
                    'nilai_rab': record.nilai_rab,
                    'total_rab': record.total_rab,
                    'note': record.note,
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

    @http.route('/api/donasi', auth='public', methods=['GET'], type='http', csrf=False)
    def get_donasi(self, **kwargs):
        try:
            donasi_records = request.env['donasi.management'].sudo().search([])
            donasi_list = []
            for record in donasi_records:
                donasi_list.append({
                    'id': record.id,
                    'nama_program': record.nama_program,
                    'saldo': record.saldo,
                    'tersalurkan': record.tersalurkan,
                    'date_begin': record.date_begin.strftime('%Y-%m-%d') if record.date_begin else '',
                    'date_end': record.date_end.strftime('%Y-%m-%d') if record.date_end else '',
                    'target_terkumpul': record.target_terkumpul,
                    'progres_saldo_terkumpul': record.progres_saldo_terkumpul,
                    'jumlah_donatur': record.jumlah_donatur,
                    'jumlah_penerima': record.jumlah_penerima,
                    'state': record.state,
                })
            return request.make_response(
                data=json.dumps({'status': 200, 'response': donasi_list, 'message': 'Success'}),
                headers={'Content-Type': 'application/json'}
            )
        except Exception as e:
            return request.make_response(
                data=json.dumps({'status': 500, 'message': 'Error: %s' % str(e)}),
                headers={'Content-Type': 'application/json'}
            )

    @http.route('/api/master_donatur/register', type='json', auth='none', methods=['POST'], csrf=False)
    def create_master_donatur(self):
        try:
            # Use request.jsonrequest to access the JSON body of the request
            data = request.jsonrequest

            # Extract the parameters from the JSON body
            nama_donatur = data.get('nama_donatur')
            email = data.get('email')
            phone = data.get('phone')
            gender = data.get('gender')
            note = data.get('note')
            kelurahan_id = data.get('kelurahan_id')
            kecamatan_id = data.get('kecamatan_id')
            kabkota_id = data.get('kabkota_id')
            provinsi_id = data.get('provinsi_id')

            # Validate required fields
            if not nama_donatur or not phone:
                return Response("Missing required fields", status=400)

            # Log incoming data for debugging
            _logger.info(f"Creating donor with name: {nama_donatur}, phone: {phone}")

            # Check for existing partner using sudo to bypass access rights
            existing_partner = request.env['res.partner'].sudo().search([
                ('name', '=', nama_donatur),
                ('phone', '=', phone),
            ], limit=1)

            if existing_partner:
                partner_id = existing_partner.id
            else:
                # Create a new res.partner with sudo
                partner_values = {
                    'name': nama_donatur,
                    'email': email,
                    'phone': phone,
                }
                new_partner = request.env['res.partner'].sudo().create(partner_values)
                partner_id = new_partner.id

            # Create master.donatur record with sudo
            donatur_values = {
                'nama_donatur': nama_donatur,
                'email': email,
                'phone': phone,
                'gender': gender,
                'note': note,
                'partner_id': partner_id,
                'kelurahan_id': kelurahan_id,
                'kecamatan_id': kecamatan_id,
                'kabkota_id': kabkota_id,
                'provinsi_id': provinsi_id,
            }

            new_donatur = request.env['master.donatur'].sudo().create(donatur_values)

            # Return success response
            return {
                'status': 'success',
                'donatur_id': new_donatur.id,
                'partner_id': partner_id,
            }
        except Exception as e:
            _logger.error(f"Error creating master donatur: {str(e)}")
            return Response("Internal Server Error", status=500)
