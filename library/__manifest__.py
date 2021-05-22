# -*- coding: utf-8 -*-
{
    'name': "library",

    'summary': """
        Library Management Software""",

    'description': """
        Library Management Software.
    """,

    'author': "My Company",
    'website': "http://www.marko.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Library',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail'],

    # always loaded
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/library_views.xml',
        'views/librarian_views.xml',
        'views/agreement_views.xml',
        'data/sequence.xml',
        'views/templates.xml',
        'reports/library_card.xml',
        'reports/librarian_card.xml',
        'reports/report.xml',
        'data/mail_template.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
    'sequence': -100,
}
