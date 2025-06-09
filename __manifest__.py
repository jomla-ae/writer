# -*- coding: utf-8 -*-
{
    'name': "Writer",

    'summary': """Writer to add description for products and product categories""",

    'description': """
        Writer to add description for products and product categories
    """,

    'author': "Qsys IT",
    'website': "http://qsys-it.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Tools',
    'version': '0.1',

    # any module necessary for this one to work correctly

    'depends': ['hr', 'product_status', 'product_brand', 'customize_jomla', 'product_multi_image_type'],
    # always loaded
    'data': [
        'data/cron.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/assign_writer_views.xml',
        'views/hr_employee_views.xml',
        'views/product_brand_views.xml',
        'views/product_tag_views.xml',
        'views/product_category_views.xml',
        'views/product_template_views.xml',
        'views/product_views.xml',
        'views/res_config_settings_views.xml',
        'views/writer_commission_line_views.xml',
        'views/writer_pricelist_views.xml',
        'views/writer_target_views.xml',
        'views/portal_templates.xml',
        'views/menus.xml'
    ],
    'assets': {
        'web.assets_frontend': [
            'writer/static/src/css/faqs.css',
            'writer/static/src/js/writer_portal.js',
            'writer/static/src/js/writer_product_brand_edit.js',
            'writer/static/src/js/writer_product_category_edit.js',
            'writer/static/src/js/writer_product_edit.js',
            'writer/static/src/js/writer_product_tag_edit.js',
            'writer/static/src/js/writer_field_many2many.js',
        ],
    },
    'license': 'LGPL-3'

}
