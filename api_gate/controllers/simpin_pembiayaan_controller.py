from odoo import http
from odoo.http import request
import json

class SimPinPembiayaanController(http.Controller):

    @http.route('/api/pembiayaan', type='http', auth='user', methods=['GET'], csrf=False)
    def get_pembiayaan(self):
        try:
            user = request.env.user
            partner = request.env['res.partner'].sudo().search([('user_id', '=', user.id)])
            member = request.env['simpin_syariah.member'].sudo().search([('partner_id', '=', partner.id)], limit=1)
            
            # Cek apakah member ditemukan
            if not member:
                response = {
                    'status': 'error',
                    'message': 'Member tidak ditemukan'
                }
                return request.make_response(json.dumps(response), headers=[('Content-Type', 'application/json')])

            # Mendapatkan pembiayaan untuk member yang login
            pembiayaan = request.env['simpin_syariah.pembiayaan'].sudo().search([('member_id', '=', member.id)])

            # Menyiapkan data pembiayaan untuk response
            pembiayaan_data = []
            for record in pembiayaan:
                pembiayaan_data.append({
                    'nomor_pinjaman': record.name,
                    'nama_anggota': record.member_id.name,
                    'peruntukan': record.peruntukan.name if record.peruntukan else '',
                    'jenis_akad': record.akad_id.name if record.akad_id else '',
                    'produk': record.product_id.name if record.product_id else '',
                    'tanggal_akad': record.tanggal_akad.strftime('%Y-%m-%d'),
                    'nilai_pinjaman': record.total_pembiayaan,
                    'periode_angsuran': record.periode_angsuran,
                    'angsuran': record.angsuran,
                    'keterangan': record.notes if record.notes else '',
                    'status_pinjaman': record.state,
                })

            # Menggabungkan respons ke dalam JSON
            response = {
                'status': 'success',
                'pembiayaan': pembiayaan_data
            }

            return request.make_response(json.dumps(response), headers=[('Content-Type', 'application/json')])

        except Exception as e:
            # Menangani error
            response = {
                'status': 'error',
                'message': str(e)
            }
            return request.make_response(json.dumps(response), headers=[('Content-Type', 'application/json')])

    @http.route('/api/pembiayaan/angsuran', type='http', auth='user', methods=['GET'], csrf=False)
    def get_angsuran_pinjaman(self):
        try:
            user = request.env.user
            partner = request.env['res.partner'].sudo().search([('user_id', '=', user.id)])
            member = request.env['simpin_syariah.member'].sudo().search([('partner_id', '=', partner.id)], limit=1)

            if not member:
                response = {
                    'status': 'error',
                    'message': 'Member not found for this user.'
                }
                return request.make_response(json.dumps(response), headers=[('Content-Type', 'application/json')])

            # Mengambil data angsuran berdasarkan member_id
            angsuran_records = request.env['account.move'].sudo().search([
                ('pembiayaan_id.member_id', '=', member.id),
                ('move_type', '=', 'out_invoice')  # Pastikan hanya mengambil angsuran
            ])

            angsuran_data = []
            for angsuran in angsuran_records:
                angsuran_data.append({
                    'id': angsuran.id,
                    'tanggal_jatuh_tempo': angsuran.invoice_date_due.strftime('%Y-%m-%d') if angsuran.invoice_date_due else '',   # Tanggal Jatuh Tempo
                    'nomor_invoice': angsuran.name,  # Nomor Invoice
                    'total_tagihan': angsuran.amount_total,  # Total Tagihan
                    'status_pembayaran': angsuran.payment_state,  # Status Pembayaran
                    'nominal_pembayaran': angsuran.amount_residual,  # Nominal Pembayaran
                })

            # Menggabungkan respons ke dalam JSON
            response = {
                'status': 'success',
                'angsuran': angsuran_data
            }

            return request.make_response(json.dumps(response), headers=[('Content-Type', 'application/json')])

        except Exception as e:
            # Menangani error
            response = {
                'status': 'error',
                'message': str(e)
            }
            return request.make_response(json.dumps(response), headers=[('Content-Type', 'application/json')])

    @http.route('/api/pembiayaan/create', type='json', auth='user', methods=['POST'], csrf=False)
    def create_pembiayaan(self):
        try:
            # Retrieve data from the request
            data = request.jsonrequest

            # Get the current user and find their partner and member information
            user = request.env.user
            partner = request.env['res.partner'].sudo().search([('user_id', '=', user.id)])
            member = request.env['simpin_syariah.member'].sudo().search([('partner_id', '=', partner.id)], limit=1)

            # Validate if member is found
            if not member:
                return {'status': 'error', 'message': 'Member not found for the logged-in user.'}

            # Required fields from the request
            akad_id = data.get('akad_id')
            product_id = data.get('product_id')
            peruntukan = data.get('peruntukan')
            periode_angsuran = data.get('periode_angsuran', 12)
            total_pembiayaan = data.get('total_pembiayaan', 5000000)

            # Optional fields
            tanggal_akad = data.get('tanggal_akad')
            biaya_lines = data.get('biaya_lines', [])
            notes = data.get('notes', '')

            # Validate that the required fields are present
            if not akad_id or not product_id or not peruntukan:
                return {'status': 'error', 'message': 'Field akad_id, product_id, and peruntukan are required.'}

            # Create financing number based on date and ID
            today = datetime.datetime.now().strftime("%Y%m%d")
            pembiayaan_name = f"PMB-{today}-{request.env['simpin_syariah.pembiayaan'].sudo().search_count([]) + 1}"

            # Create the new pembiayaan
            pembiayaan = request.env['simpin_syariah.pembiayaan'].sudo().create({
                'name': pembiayaan_name,
                'member_id': member.id,
                'akad_id': akad_id,
                'product_id': product_id,
                'peruntukan': peruntukan,
                'periode_angsuran': periode_angsuran,
                'total_pembiayaan': total_pembiayaan,
                'tanggal_akad': tanggal_akad,
                'biaya_lines': [(0, 0, line) for line in biaya_lines],  # Add biaya lines if provided
                'notes': notes,
            })

            # If successfully created, return a success response
            return {
                'status': 'success',
                'message': 'Pembiayaan successfully created',
                'data': {
                    'id': pembiayaan.id,
                    'name': pembiayaan.name,
                }
            }

        except Exception as e:
            return {'status': 'error', 'message': str(e)}
