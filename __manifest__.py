# -*- coding: utf-8 -*-
{
    'name': "Campos de Clientes",

    'summary': """Campos personalizados para clientes de Vittal.""",

    'description': """
        Campos personalizados para clientes de Vittal. Depende del modulo de ventas.
    """,

    'author': "Prescrypto",
    'website': "http://www.prescrypto.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Specific Industry Applications',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'crm',
        'stock',
        'mrp',
        'sale',
        'point_of_sale',
        'account',
        'account_accountant',
        'contacts',
        'board'
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # styles
    'css': [
        'static/src/css/custom.css'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
