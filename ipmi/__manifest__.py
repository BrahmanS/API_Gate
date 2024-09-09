{
    'name': 'Ipmi Tema',
    'version': '1.0',
    'category': 'Website',
    'author': 'Ahmad al fajri',
    'summary': 'Tema odoo ipmi',
    'depends': ['website'],
    'data': [
        'views/templates.xml',
        'views/homepage.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'ipmi/static/src/scss/style.scss',
            'ipmi/static/src/js/main.js',
           
        ],
    },
     'images': [
        'ipmi/static/src/img/ipmi_logo.png',
        'ipmi/static/src/img/badge1.jpg',
        'ipmi/static/src/img/badge2.jpg', 
        'ipmi/static/src/img/badge3.jpg',
        'ipmi/static/src/img/image.png',
    ], 
    'installable': True,
    'application': False,
}