from odoo import http
from odoo.http import request, Response
import json
import datetime


class SimPinPeminjamanController(http.Controller):

    @http.route('/api/pinjaman', type='http', auth='user', methods=['GET'], csrf=False)
    def get_pinjaman(self):
        try:
            user = request.env.user
            partner = request.env['res.partner'].sudo().search([('user_id', '=', user.id)])
            member = request.env['simpin_syariah.member'].sudo().search([('partner_id', '=', partner.id)], limit=1)

            if not member:
                response = {
                    'status': 'error',
                    'message': 'Member not found'
                }
                return request.make_response(json.dumps(response), headers=[('Content-Type', 'application/json')])

            pinjaman_records = request.env['simpin_syariah.pinjaman'].sudo().search([('member_id', '=', member.id)])

            pinjaman_data = []
            for pinjaman in pinjaman_records:
                pinjaman_data.append({
                    'nomor_pinjaman': pinjaman.name,
                    'nama_anggota': member.name,  # Nama anggota
                    'peruntukan': pinjaman.peruntukan.name if pinjaman.peruntukan else '',
                    'jenis_akad': pinjaman.akad_id.name if pinjaman.akad_id else '',
                    'produk': pinjaman.product_id.name if pinjaman.product_id else '',
                    'tanggal_akad': pinjaman.tanggal_akad.strftime('%Y-%m-%d') if pinjaman.tanggal_akad else '',
                    'nilai_pinjaman': pinjaman.nilai_pinjaman,
                    'periode_angsuran': pinjaman.periode_angsuran,
                    'angsuran': pinjaman.angsuran,
                    'keterangan': pinjaman.notes,
                    'state': pinjaman.state,
                })

            response = {
                'status': 'success',
                'pinjaman': pinjaman_data
            }

            return request.make_response(json.dumps(response), headers=[('Content-Type', 'application/json')])

        except Exception as e:
            # Menangani error
            response = {
                'status': 'error',
                'message': str(e)
            }
            return request.make_response(json.dumps(response), headers=[('Content-Type', 'application/json')])


    
    @http.route('/api/pinjaman/angsuran', type='http', auth='user', methods=['GET'], csrf=False)
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
                ('pinjaman_id.member_id', '=', member.id),
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


    @http.route('/api/akad_pinjaman', type='http', auth='none', methods=['GET'], csrf=False)
    def get_akad(self):
        try:
            # Domain untuk mencari akad sesuai dengan ketentuan
            domain = [
                ('is_actived', '=', True),
                '|',
                ('category_id.parent_id.name', '=', 'Pinjaman'),
                ('category_id.name', '=', 'Pinjaman')
            ]
            
            # Query Odoo untuk mendapatkan akad berdasarkan domain
            akad_records = request.env['master.akad_syariah'].sudo().search(domain)
            
            # Menyiapkan data untuk response
            akad_data = []
            for akad in akad_records:
                akad_data.append({
                    'id': akad.id,
                    'name': akad.name,
                    'category_name': akad.category_id.name,
                    'parent_category_name': akad.category_id.parent_id.name if akad.category_id.parent_id else '',
                    'is_actived': akad.is_actived,
                })
            
            # Menggabungkan respons ke dalam JSON
            response = {
                'status': 'success',
                'message': 'Akad retrieved successfully',
                'data': akad_data
            }

            return request.make_response(json.dumps(response), headers=[('Content-Type', 'application/json')])

        except Exception as e:
            # Menangani error
            return request.make_response(json.dumps({'status': 'error', 'message': str(e)}), headers=[('Content-Type', 'application/json')])

    @http.route('/api/products_pinjaman', type='http', auth='none', methods=['GET'], csrf=False)
    def get_products(self):
        try:
            # Domain untuk mencari produk sesuai dengan ketentuan
            domain = [
                ('is_syariah', '=', True),
                '|',
                ('product_tmpl_id.categ_id.parent_id.name', '=', 'Pinjaman'),
                ('product_tmpl_id.categ_id.name', '=', 'Pinjaman')
            ]
            
            # Query Odoo untuk mendapatkan produk berdasarkan domain
            products = request.env['product.product'].sudo().search(domain)
            
            # Menyiapkan data untuk response
            product_data = []
            for product in products:
                product_data.append({
                    'id': product.id,
                    'name': product.name,
                    'categ_id': product.product_tmpl_id.categ_id.name,
                    'parent_categ_name': product.product_tmpl_id.categ_id.parent_id.name if product.product_tmpl_id.categ_id.parent_id else '',
                    'is_syariah': product.is_syariah,
                })
            
            # Menggabungkan respons ke dalam JSON
            response = {
                'status': 'success',
                'message': 'Products retrieved successfully',
                'data': product_data
            }

            return request.make_response(json.dumps(response), headers=[('Content-Type', 'application/json')])

        except Exception as e:
            # Menangani error
            return request.make_response(json.dumps({'status': 'error', 'message': str(e)}), headers=[('Content-Type', 'application/json')])


    
    @http.route('/api/pinjaman/create', type='json', auth='user', methods=['POST'], csrf=False)
    def create_pinjaman(self):
        try:
            # Mengambil data dari request.jsonrequest
            data = request.jsonrequest

            # Mengambil user yang sedang login dan mencari partner serta member terkait
            user = request.env.user
            partner = request.env['res.partner'].sudo().search([('user_id', '=', user.id)])
            member = request.env['simpin_syariah.member'].sudo().search([('partner_id', '=', partner.id)], limit=1)

            # Validasi apakah member ditemukan
            if not member:
                return {'status': 'error', 'message': 'Member tidak ditemukan untuk pengguna yang sedang login.'}

            # Required fields
            akad_id = data.get('akad_id')
            product_id = data.get('product_id')
            peruntukan = data.get('peruntukan')
            periode_angsuran = data.get('periode_angsuran', 12)
            nilai_pinjaman = data.get('nilai_pinjaman', 5000000)

            # Optional fields
            tanggal_akad = data.get('tanggal_akad')
            biaya_lines = data.get('biaya_lines', [])
            notes = data.get('notes', '')

            # Validasi bahwa field wajib ada
            if not akad_id or not product_id or not peruntukan:
                return {'status': 'error', 'message': 'Field akad_id, product_id, dan peruntukan diperlukan.'}

            # Membuat nomor pinjaman berdasarkan ID dan tanggal
            today = datetime.datetime.now().strftime("%Y%m%d")
            pinjaman_name = f"PNJ-{today}-{request.env['simpin_syariah.pinjaman'].sudo().search_count([]) + 1}"

            # Membuat pinjaman baru
            pinjaman = request.env['simpin_syariah.pinjaman'].sudo().create({
                'name': pinjaman_name,
                'member_id': member.id,  # Menggunakan member.id yang ditemukan
                'akad_id': akad_id,
                'product_id': product_id,
                'peruntukan': peruntukan,
                'periode_angsuran': periode_angsuran,
                'nilai_pinjaman': nilai_pinjaman,
                'tanggal_akad': tanggal_akad,
                'biaya_lines': [(0, 0, line) for line in biaya_lines],  # Tambahkan komponen biaya
                'notes': notes,
            })

            # Jika berhasil dibuat, return success response
            return {
                'status': 'success',
                'message': 'Pinjaman berhasil dibuat',
                'data': {
                    'id': pinjaman.id,
                    'name': pinjaman.name,
                }
            }

        except Exception as e:
            return {'status': 'error', 'message': str(e)}



