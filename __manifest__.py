# -*- coding: utf-8 -*-
{
    "name": "Writer",
    "summary": """To manage writing metadata for products""",
    "author": "Jomla",
    "website": "https://github.com/jomla-ae",
    "category": "Inventory",
    "version": "0.1",
    "depends": ["base", "product_status", "product_brand", "customize_jomla", "product_multi_image_type", "widget_ckeditor"],
    "data": [
        # cron
        "data/cron.xml",
        # security
        "security/security.xml",
        "security/ir.model.access.csv",
        # backend views
        "views/res_users_views.xml",
        "views/product_template_views.xml",
        "views/product_product_views.xml",
        "views/res_config_settings_views.xml",
        "views/writer_commission_line_views.xml",
        "views/writer_pricelist_views.xml",
        "views/writer_target_views.xml",
        "views/portal_templates.xml",
        "views/menus.xml",
        # portal templates
        "views/product_template_templates.xml",
        "views/writer_commission_line_templates.xml",
        "views/writer_target_templates.xml",
        # wizards
        "wizard/assign_writer_views.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "writer/static/src/css/faqs.css",
            "writer/static/src/js/writer_portal.js",
            "writer/static/src/js/writer_product_edit.js",
            "writer/static/src/js/column_toggle.js",
        ],
    },
    "application": True,
    "license": "LGPL-3",
}
