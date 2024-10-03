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
        
    @http.route('/api/wakaf/<int:wakaf_id>', auth='public', methods=['GET'], type='http', csrf=False)
    def get_wakaf_id(self, wakaf_id):
        try:
            # Fetch the wakaf Management record
            record = request.env['wakaf.management'].sudo().browse(wakaf_id)
            if not record.exists():
                return self._json_response({'status': 404, 'message': 'wakaf not found'})

            # Fetch RAB wakaf Line records
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

            # # Fetch Register wakaf Donatur records
            # donatur_lines = record.donatur_wakaf_ids
            # donatur_wakaf_data = []
            # for donatur in donatur_lines:
            #     donatur_data = {
            #         'id': donatur.id,
            #         'product_id': donatur.product_id.id,
            #         'product_name': donatur.product_id.name,
            #         'donatur_id': donatur.donatur_id.id,
            #         'donatur_name': donatur.donatur_id.nama_wakaf_donatur,
            #         'email': donatur.email,
            #         'phone': donatur.phone,
            #         'infaq_date': donatur.infaq_date.strftime('%Y-%m-%d') if donatur.infaq_date else '',
            #         'nilai_wakaf': donatur.nilai_wakaf,
            #         'total_wakaf': donatur.total_wakaf,
            #         'note': donatur.note,
            #         'partner_id': donatur.partner_id.id,
            #         'qty': donatur.qty,
            #     }
            #     donatur_wakaf_data.append(donatur_data)

            # Compile wakaf Management data
            wakaf_data = {
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

            return self._json_response({'status': 200, 'response': wakaf_data, 'message': 'Success'})

        except Exception as e:
            _logger.error(f"Error fetching wakaf data: {str(e)}")
            return self._json_response({'status': 500, 'message': f'Error: {str(e)}'})


    def _json_response(self, data):
        return request.make_response(
            data=json.dumps(data),
            headers={'Content-Type': 'application/json'}
        )

    @http.route('/api/wakaf_donatur/register', type='json', auth='public', methods=['POST'], csrf=False)
    def create_wakaf_donatur(self):
        try:
            # Get JSON request data
            data = request.jsonrequest

            # Extract parameters
            nama_wakaf_donatur = data.get('nama_wakaf_donatur')
            email = data.get('email')
            phone = data.get('phone')
            gender = data.get('gender', '')
            note = data.get('note', '')
            nilai_wakaf = data.get('nilai_wakaf')
            wakaf_id = data.get('wakaf_id')
            infaq_date = data.get('infaq_date', datetime.today().strftime('%Y-%m-%d'))
            rab_line_id = data.get('rab_line_id')

            # Validate required fields
            if not nama_wakaf_donatur or not phone or not nilai_wakaf or not wakaf_id or not infaq_date:
                return {'status': 400, 'message': "Missing required fields"}

            # Log incoming data for debugging
            _logger.info(f"Creating donor with name: {nama_wakaf_donatur}, phone: {phone}")

            partner_id = None

            # Check for existing master.donatur
            existing_donatur = request.env['master.wakaf.donatur'].sudo().search([
                ('nama_wakaf_donatur', '=', nama_wakaf_donatur),
                ('email', '=', email),
                ('phone', '=', phone),
            ], limit=1)

            if existing_donatur:
                new_donatur = existing_donatur
                partner_id = existing_donatur.partner_id.id
            else:
                # Check for existing partner using sudo to bypass access rights
                existing_partner = request.env['res.partner'].sudo().search([
                    ('name', '=', nama_wakaf_donatur),
                    ('phone', '=', phone),
                ], limit=1)

                if existing_partner:
                    partner_id = existing_partner.id
                else:
                    # Create a new res.partner with sudo
                    partner_values = {
                        'name': nama_wakaf_donatur,
                        'email': email,
                        'phone': phone,
                    }
                    new_partner = request.env['res.partner'].sudo().create(partner_values)
                    partner_id = new_partner.id

                # Create master.wakaf.donatur record with sudo
                donatur_values = {
                    'nama_wakaf_donatur': nama_wakaf_donatur,
                    'email': email,
                    'phone': phone,
                    'gender': gender,
                    'note': note,
                    'partner_id': partner_id,
                }

                new_donatur = request.env['master.wakaf.donatur'].sudo().create(donatur_values)

            # Ensure partner_id is not None
            if not partner_id:
                return {'status': 500, 'message': "Failed to create or retrieve partner_id"}

            rab_line = request.env['rab.wakaf.line'].sudo().search([
                ('id', '=', rab_line_id)
            ])
            
            # Create register.wakaf.donatur record with sudo
            wakaf_values = {
                'wakaf_id': wakaf_id,
                'product_id': rab_line.product_id.id,
                'wakaf_donatur_id': new_donatur.id,
                'infaq_date': infaq_date,
                'nilai_wakaf': nilai_wakaf,
                'qty': 1,  # Default quantity to 1
                'note': note,
            }

            wakaf_record = request.env['register.wakaf.donatur'].sudo().create(wakaf_values)

            # Create sale order and sale order line
            sale_order_values = {
                'partner_id': partner_id,
                'date_order': infaq_date,
                'wakaf_id': wakaf_id,
            }
            sale_order = request.env['sale.order'].sudo().create(sale_order_values)

            sale_order_line_values = {
                'product_id': rab_line.product_id.id,
                'name': note,
                'price_unit': nilai_wakaf,
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
                'message': 'Donatur, wakaf, Sale Order, and Sale Order Line created successfully',
                'donatur_id': new_donatur.id,
                'wakaf_record_id': wakaf_record.id,
                'sale_order_id': sale_order.id,
                'sale_order_line_id': sale_order_line.id,
                'partner_id': partner_id,
                'sale_order_name': sale_order.name
            }

        except Exception as e:
            _logger.error(f"Error creating donatur and wakaf: {str(e)}")
            return {'status': 500, 'message': f"Internal Server Error: {str(e)}"}
