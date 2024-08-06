# -*- coding: utf-8 -*-
{
    "name": "Donasi",
    "version": "1.01",
    "author": "AFajar",
    "license": "",
    "category": "Custom",
    "summary": "Modul Donasi",
    "website": "",
    "depends": ['mail', 'base', 'contacts', 'sale', 'purchase', 'asa_wilayah', 'stock'],
    "data": [
        'data/dontur_sequence.xml',
        'security/ir.model.access.csv',
        'views/menu.xml',
        
        'views/master_program_donasi_views.xml',
        'views/master_donatur_views.xml',
        'views/master_penerima_views.xml',
        'views/master_tipe_penerima_views.xml',
        'views/register_donasi_donatur_views.xml',
        'views/register_penerima_views.xml',
        'views/register_wakaf_donatur_views.xml',
        'views/wilayah_views.xml',
        'views/wakaf_views.xml',
        'views/master_category_views.xml',
        'views/master_program_wakaf_views.xml',
        'views/master_tipe_wakaf_views.xml',
        'views/master_wakaf_donatur_views.xml',
        'views/master_tipe_donatur_views.xml',
        'views/donasi_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}