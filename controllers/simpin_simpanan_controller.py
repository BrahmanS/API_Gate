from odoo import http
from odoo.http import request
import json

class SimPinSimpananController(http.Controller):

    @http.route('/api/simpanan', type='http', auth='user', methods=['GET'], csrf=False)
    def get_rekening(self):
        try:
            user = request.env.user
            partner = request.env['res.partner'].sudo().search([('user_id', '=', user.id)])
            member = request.env['simpin_syariah.member'].sudo().search([('partner_id', '=', partner.id)], limit=1)

            
            if not member:
                response = {
                    'status': 'error',
                    'message': 'Member tidak ditemukan'
                }
                return request.make_response(json.dumps(response), headers=[('Content-Type', 'application/json')])

            
            rekening = request.env['simpin_syariah.rekening'].sudo().search([('member_id', '=', member.id)])

            
            rekening_data = []
            for rec in rekening:
                rekening_data.append({
                    'nomor_rekening': rec.name,
                    'nama_anggota': rec.member_id.name,
                    'jenis_akad': rec.akad_id.name if rec.akad_id else '',
                    'produk': rec.product_id.name,
                    'balance': rec.balance,
                })

            
            response = {
                'status': 'success',
                'rekening': rekening_data
            }

            return request.make_response(json.dumps(response), headers=[('Content-Type', 'application/json')])

        except Exception as e:
            # Menangani error
            response = {
                'status': 'error',
                'message': str(e)
            }
            return request.make_response(json.dumps(response), headers=[('Content-Type', 'application/json')])


    @http.route('/api/simpanan/angsuran', type='http', auth='user', methods=['GET'], csrf=False)
    def get_angsuran_simpanan(self):
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
                ('simpanan_id.member_id', '=', member.id),
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



    @http.route('/api/simpanan/vendor', type='http', auth='user', methods=['GET'], csrf=False)
    def get_simpanan_vendor(self):
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
                ('simpanan_id.member_id', '=', member.id),
                ('move_type', '=', 'in_invoice')  # Pastikan hanya mengambil angsuran
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


    @http.route('/api/simpanan/transaksi', type='http', auth='user', methods=['GET'], csrf=False)
    def get_transaksi_simpanan(self):
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

            rekening = request.env['simpin_syariah.rekening'].sudo().search([('member_id', '=', member.id)], limit=1)
            if not rekening:
                return request.make_response(json.dumps({
                    'status': 'error',
                    'message': 'Rekening tidak ditemukan untuk member ini.'
                }), headers=[('Content-Type', 'application/json')])

            # Ambil data rekening lines terkait
            rekening_lines = request.env['simpin_syariah.rekening.line'].sudo().search([('rekening_id', '=', rekening.id)])

            rekening_lines_data = []
            for line in rekening_lines:
                rekening_lines_data.append({
                    'id': line.id,
                    'rekening_nomor': line.rekening_id.name,
                    'tanggal': line.tanggal.strftime('%Y-%m-%d'),
                    'debit': line.debit,
                    'credit': line.credit,
                    'balance': line.balance,
                    'keterangan': line.keterangan,
                    'state': line.state,
                    'sandi_id': line.sandi_id.name if line.sandi_id else '',
                    'rek_asal': line.rek_asal.name if line.rek_asal else '',
                    'rek_tujuan': line.rek_tujuan.name if line.rek_tujuan else '',
                })

            # Mengembalikan data transaksi dalam format JSON
            response = {
                'status': 'success',
                'rekening_lines': rekening_lines_data
            }
            return request.make_response(json.dumps(response), headers=[('Content-Type', 'application/json')])

        except Exception as e:
            # Error handling
            return request.make_response(json.dumps({
                'status': 'error',
                'message': str(e)
            }), headers=[('Content-Type', 'application/json')])
