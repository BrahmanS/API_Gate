from odoo import http, fields
from odoo.http import request, Response
import json
import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class DonationController(http.Controller):

    @http.route('/api/donasi', auth='public', methods=['GET'], type='http', csrf=False)
    def get_donasi(self, **kwargs):
        try:
            # Get current date
            current_date = fields.Date.today()

            donasi_records = request.env['donasi.management'].sudo().search([
                ('state', '=', 'publish'),
                '|', '|',
                ('date_end', '>=', current_date),
                ('date_end', '=', False),
                '&', ('date_end', '>=', current_date), ('write_date', '>', current_date - timedelta(days=1))
            ])
            
            donasi_list = []
            for record in donasi_records:
                donasi_list.append({
                    'id': record.id,
                    'nama_program': record.nama_program,
                    'yayasan': record.yayasan_id.name,
                    'saldo': record.saldo,
                    'tersalurkan': record.tersalurkan,
                    'date_begin': record.date_begin.strftime('%Y-%m-%d') if record.date_begin else '',
                    'date_end': record.date_end.strftime('%Y-%m-%d') if record.date_end else '',
                    'target_terkumpul': record.target_terkumpul,
                    'progres_saldo_terkumpul': record.progres_saldo_terkumpul,
                    'jumlah_donatur': record.jumlah_donatur,
                    'jumlah_penerima': record.jumlah_penerima,
                    'keterangan': record.keterangan,
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

        
    @http.route('/api/donasi/<int:donasi_id>', auth='public', methods=['GET'], type='http', csrf=False)
    def get_donasi_id(self, donasi_id):
        try:
            # Fetch the Donasi Management record
            record = request.env['donasi.management'].sudo().browse(donasi_id)
            if not record.exists():
                return self._json_response({'status': 404, 'message': 'Donasi not found'})

            # Fetch RAB Donasi Line records
            rab_lines = record.rab_donasi_ids
            rab_donasi_data = []
            for rab in rab_lines:
                rab_data = {
                    'id': rab.id,
                    'product_id': rab.product_id.id,
                    'product_name': rab.product_id.name,
                    'qty': rab.qty,
                    'uom_id': rab.uom_id.id,
                    'uom_name': rab.uom_id.name,
                    'deskripsi': rab.deskripsi,
                    'nilai_paket': rab.nilai_paket,
                    'total_paket': rab.total_paket,
                }
                rab_donasi_data.append(rab_data)

            # Fetch Register Donasi Donatur records
            donatur_lines = record.donatur_donasi_ids
            donatur_donasi_data = []
            for donatur in donatur_lines:
                donatur_data = {
                    'id': donatur.id,
                    'product_id': donatur.product_id.id,
                    'product_name': donatur.product_id.name,
                    'donatur_id': donatur.donatur_id.id,
                    'donatur_name': donatur.donatur_id.nama_donatur,
                    'email': donatur.email,
                    'phone': donatur.phone,
                    'infaq_date': donatur.infaq_date.strftime('%Y-%m-%d') if donatur.infaq_date else '',
                    'nilai_donasi': donatur.nilai_donasi,
                    'total_donasi': donatur.total_donasi,
                    'note': donatur.note,
                    'partner_id': donatur.partner_id.id,
                    'qty': donatur.qty,
                }
                donatur_donasi_data.append(donatur_data)

            # Compile Donasi Management data
            donasi_data = {
                'id': record.id,
                'nama_program': record.nama_program,
                'yayasan': record.yayasan_id.name,
                'saldo': record.saldo,
                'tersalurkan': record.tersalurkan,
                'date_begin': record.date_begin.strftime('%Y-%m-%d') if record.date_begin else '',
                'date_end': record.date_end.strftime('%Y-%m-%d') if record.date_end else '',
                'target_terkumpul': record.target_terkumpul,
                'progres_saldo_terkumpul': record.progres_saldo_terkumpul,
                'jumlah_donatur': record.jumlah_donatur,
                'jumlah_penerima': record.jumlah_penerima,
                'keterangan': record.keterangan,
                'state': record.state,
                'rab_donasi': rab_donasi_data,
                'donatur_donasi': donatur_donasi_data,
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

    

    @http.route('/api/donatur_and_donasi/register', type='json', auth='public', methods=['POST'], csrf=False)
    def create_donatur_and_donasi(self):
        try:
            # Get JSON request data
            data = request.jsonrequest

            # Extract parameters
            nama_donatur = data.get('nama_donatur')
            email = data.get('email')
            phone = data.get('phone')
            gender = data.get('gender', '')
            note = data.get('note', '')
            nilai_donasi = data.get('nilai_donasi')
            donasi_id = data.get('donasi_id')
            infaq_date = data.get('infaq_date', datetime.today().strftime('%Y-%m-%d'))

            # Validate required fields
            if not nama_donatur or not phone or not nilai_donasi or not donasi_id or not infaq_date:
                return {'status': 400, 'message': "Missing required fields"}

            # Log incoming data for debugging
            _logger.info(f"Creating donor with name: {nama_donatur}, phone: {phone}")

            # Check for existing master.donatur
            existing_donatur = request.env['master.donatur'].sudo().search([
                ('nama_donatur', '=', nama_donatur),
                ('email', '=', email),
                ('phone', '=', phone),
            ], limit=1)

            if existing_donatur:
                new_donatur = existing_donatur
                partner_id = existing_donatur.partner_id.id
            else:
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
                }

                new_donatur = request.env['master.donatur'].sudo().create(donatur_values)

            # Fetch the first product_id from rab.donasi.line that matches the donasi_id
            rab_line = request.env['rab.donasi.line'].sudo().search([
                ('donasi_management_id', '=', donasi_id)
            ], limit=1)

            # Log RAB line search result
            _logger.info(f"RAB line search result for donasi_id {donasi_id}: {rab_line}")

            if not rab_line:
                return {'status': 400, 'message': "No RAB line found for the given donasi_id"}

            product_id = rab_line.product_id.id

            # Create register.donasi.donatur record with sudo
            donasi_values = {
                'donasi_id': donasi_id,
                'product_id': product_id,
                'donatur_id': new_donatur.id,
                'infaq_date': infaq_date,
                'nilai_donasi': nilai_donasi,
                'qty': 1,  # Default quantity to 1
                'note': note,
            }

            donasi_record = request.env['register.donasi.donatur'].sudo().create(donasi_values)

            # Create sale order and sale order line
            sale_order_values = {
                'partner_id': partner_id,
                'date_order': infaq_date,
                'donasi_id': donasi_id,
            }
            sale_order = request.env['sale.order'].sudo().create(sale_order_values)

            sale_order_line_values = {
                'product_id': product_id,
                'name': note,
                'price_unit': nilai_donasi,
                'product_uom_qty': 1,
                'order_id': sale_order.id,
            }
            sale_order_line = request.env['sale.order.line'].sudo().create(sale_order_line_values)

            # Confirm the sale order and create the invoice
            sale_order.action_confirm()
            invoice = sale_order._create_invoices()
            if invoice:
                invoice.write({'state': 'draft'})

            # Return success response
            return {
                'status': 'success',
                'message': 'Donatur, Donasi, Sale Order, and Sale Order Line created successfully',
                'donatur_id': new_donatur.id,
                'donasi_record_id': donasi_record.id,
                'sale_order_id': sale_order.id,
                'sale_order_line_id': sale_order_line.id,
                'partner_id': partner_id,
                'sale_order_name':sale_order.name
            }

        except Exception as e:
            _logger.error(f"Error creating donatur and donasi: {str(e)}")
            return {'status': 500, 'message': f"Internal Server Error: {str(e)}"}
    
    @http.route('/api/account_move/set_paid', type='json', auth='public', methods=['POST'], csrf=False)
    def set_account_move_paid(self):
        try:
            # Get JSON request data
            data = request.jsonrequest

            # Extract parameters
            sale_order_name = data.get('sale_order_name')

            # Validate required fields
            if not sale_order_name:
                return {'status': 400, 'message': "Missing required fields: 'sale_order_name'"}

            # Log incoming data for debugging
            _logger.info(f"Searching for account.move with invoice_origin based on sale order name: {sale_order_name}")

            # Search for the account.move record where invoice_origin matches the sale order name
            account_move = request.env['account.move'].sudo().search([
                ('invoice_origin', '=', sale_order_name)
            ], limit=1)

            # Check if the account.move record is found
            if not account_move:
                return {'status': 404, 'message': f"No account.move record found for sale order name: {sale_order_name}"}

            # Update the payment_state to 'paid'
            account_move.sudo().write({'payment_state': 'paid'})

            # Log the update
            _logger.info(f"Updated account.move with ID {account_move.id}, set payment_state to 'paid'")

            # Return success response
            return {
                'status': 'success',
                'message': f"Payment state updated to 'paid' for account.move with ID {account_move.id}",
                'account_move_id': account_move.id
            }

        except Exception as e:
            _logger.error(f"Error updating payment state: {str(e)}")
            return {'status': 500, 'message': f"Internal Server Error: {str(e)}"}

