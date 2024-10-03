from odoo import http
from odoo.http import request
from odoo.exceptions import UserError, ValidationError
import json
import base64
from odoo.exceptions import AccessDenied
from werkzeug.exceptions import Unauthorized

class AnggotaSyariahController(http.Controller):

    @http.route('/api/simpin_syariah/member', auth='public', methods=['POST'], type='json', csrf=False)
    def create_simpin_syariah_member(self, **kwargs):
        try:
            # Extract data from the request
            data = request.jsonrequest

            # Validate mandatory fields
            mandatory_fields = ['name', 'email', 'no_hp']
            for field in mandatory_fields:
                if field not in data or not data[field]:
                    return {'status': 'error', 'message': f'Mandatory field {field} is missing or empty.'}

            # Process files if they exist
            file_fields = ['ktp', 'ktpPasangan', 'kartuKeluarga', 'dokumenLainnya']
            for field in file_fields:
                if field in data and data[field]:
                    # Decode Base64 to binary data
                    data[field] = base64.b64decode(data[field])

            # Prepare data for creating the member record
            member_vals = {
                'name': data.get('name'),
                'company_id': data.get('company_id', request.env.user.company_id.id),
                'email': data.get('email'),
                'no_hp': data.get('no_hp'),
                'mitra_id': data.get('mitra_id'),
                'nomor_induk': data.get('nomor_induk'),
                'address': data.get('address'),
                'rukun_tetangga': data.get('rukun_tetangga'),
                'rukun_warga': data.get('rukun_warga'),
                'kelurahan_id': data.get('kelurahan_id'),
                'kecamatan_id': data.get('kecamatan_id'),
                'kabkota_id': data.get('kabkota_id'),
                'provinsi_id': data.get('provinsi_id'),
                'kodepos': data.get('kodepos'),
                'tempat_lahir': data.get('tempat_lahir'),
                'tanggal_lahir': data.get('tanggal_lahir'),
                'type_identitas': data.get('type_identitas'),
                'agama': data.get('agama'),
                'gender': data.get('gender'),
                'marital': data.get('marital'),
                'jabatan': data.get('jabatan'),
                'no_identitas': data.get('no_identitas'),
                'npwp': data.get('npwp'),
                'divisi': data.get('divisi'),
                'status_karyawan': data.get('status_karyawan'),
                'jangka_waktu_kontrak': data.get('jangka_waktu_kontrak'),
                'akhir_kontrak': data.get('akhir_kontrak'),
                'nama_atasan': data.get('nama_atasan'),
                'jabatan_atasan': data.get('jabatan_atasan'),
                'no_telp': data.get('no_telp'),
                'no_keluarga': data.get('no_keluarga'),
                'bank_id': data.get('bank_id'),
                'bank_norek': data.get('bank_norek'),
                'bank_namarek': data.get('bank_namarek'),
                'is_sukarela': data.get('is_sukarela'),
                # Save files as binary
                'upload_ktp': data.get('ktp'),
                'upload_ktp_pasangan': data.get('ktpPasangan'),
                'upload_kk': data.get('kartuKeluarga'),
                'upload_dok_lain': data.get('dokumenLainnya'),
            }

            # Create the member record
            new_member = request.env['simpin_syariah.member'].sudo().create(member_vals)

            # Return success response
            return {'status': 'success', 'message': 'Member created successfully', 'member_id': new_member.id}

        except Exception as e:
            return {'status': 'error', 'message': str(e)}



    

    @http.route('/api/banks', type='http', auth='public', methods=['GET'], csrf=False)
    def get_active_banks(self):
        try:
            # Mengambil data bank yang statusnya aktif
            active_banks = request.env['res.bank'].sudo().search([('active', '=', True)])
            bank_data = [{'id': bank.id, 'name': bank.name} for bank in active_banks]

            # Mengembalikan respons dalam format JSON
            response = {
                'status': 'success',
                'banks': bank_data
            }

            return request.make_response(json.dumps(response), headers=[('Content-Type', 'application/json')])

        except Exception as e:
            # Jika ada error, kembalikan pesan error dalam format JSON
            return request.make_response(json.dumps({'status': 'error', 'message': str(e)}), headers=[('Content-Type', 'application/json')])
    
    @http.route('/api/member/login', type='json', auth="none", methods=['POST'], csrf=False)
    def member_login(self, db, login, password, base_location=None):
        # Autentikasi standar Odoo
        try:
            request.session.authenticate(db, login, password)
        except Exception as e:
            return {'status': 'error', 'message': 'Invalid login credentials'}

        # Mendapatkan user yang sedang login
        user = request.env.user

        # Memeriksa apakah user adalah member
        member = request.env['simpin_syariah.member'].sudo().search([('partner_id', '=', user.partner_id.id)], limit=1)
        if not member:
            # Jika user bukan member, logout session dan kembalikan error
            request.session.logout()
            return {'status': 'error', 'message': 'User is not a member'}

        # Jika berhasil login dan user adalah member, kembalikan data session
        session_info = request.env['ir.http'].session_info()


        return {'status': 'success', 'session_info': session_info}

