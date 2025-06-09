# -*- coding: utf-8 -*-

import json
from datetime import datetime
from operator import itemgetter


from odoo import http
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.addons.web.controllers.export import ExcelExport
from odoo.http import request
from odoo.tools import groupby as groupbyelem

from . import writer_product, writer_commission, writer_target


class WriterPortal(CustomerPortal):
    @http.route(["/my/writer_products", "/my/writer_products/page/<int:page>"], type="http", auth="user", website=True)
    def get_products(self, page=1, search=None, search_in="all", groupby="none"):
        domain = writer_product.get_search_domain(search_in, search)
        if not domain:
            search = None
            search_in = "all"

        product_template_obj = request.env["product.template"]

        writer_products_count = product_template_obj.search_count(domain)

        groupby_mapping = writer_product.get_groupby_mapping()
        group = groupby_mapping.get(groupby)
        if not group:
            groupby = "none"

        pager = portal_pager(
            url="/my/writer_products",
            url_args={
                "groupby": groupby,
                "search_in": search_in,
                "search": search,
            },
            total=writer_products_count,
            page=page,
            step=self._items_per_page,
        )

        writer_products = product_template_obj.search(domain, limit=self._items_per_page, offset=pager["offset"])

        request.session["my_writer_products_history"] = writer_products.ids[:100]

        if group:
            grouped_products = [product_template_obj.concat(*g) for k, g in groupbyelem(writer_products, itemgetter(group))]
        else:
            grouped_products = writer_products

        return request.render(
            "writer.portal_my_writer_products",
            {
                "page_name": "Writer Products",
                "pager": pager,
                "default_url": "/my/writer_products",
                "searchbar_groupby": writer_product.get_searchbar_groupby(),
                "searchbar_inputs": writer_product.get_searchbar_inputs(),
                "search": search,
                "search_in": search_in,
                "groupby": groupby,
                "grouped_products": grouped_products,
            },
        )

    @http.route(["/my/writer_products/edit/<int:id>"], type="http", auth="user", methods=["GET", "POST"], website=True, csrf=False)
    def edit_product(self, id):
        product = request.env["product.template"].browse(id)
        if not product.exists():
            raise http.NotFound()

        lang_code_en = request.env.ref("base.lang_en").code
        lang_ar = request.env.ref("base.lang_ar")
        lang_code_ar = False
        if lang_ar.active:
            lang_code_ar = lang_ar.code

        if request.httprequest.method == "GET":
            return request.render(
                "writer.portal_my_writer_product_edit",
                {
                    "page_name": "Writer Product",
                    "product": product,
                    "lang_code_en": lang_code_en,
                    "lang_code_ar": lang_code_ar,
                },
            )

        data = request.httprequest.form

        product.with_context(lang=lang_code_en).write(
            {
                "name": data.get("name", False),
                "description": data.get("description", False),
                "description_arabic": data.get("description_arabic", False),
                "seo_title": data.get("seo_title", False),
                "seo_description": data.get("seo_description", False),
            }
        )

        if lang_code_ar:
            product.with_context(lang=lang_code_ar).write(
                {
                    "name": data.get("name_arabic", False),
                    "seo_title": data.get("seo_title_arabic", False),
                    "seo_description": data.get("seo_description_arabic", False),
                }
            )

        if data.get("submit_option", False):
            product.action_submit()

        return request.redirect("/my/writer_products")

    @http.route(["/my/writer_products/submit/<int:id>"], type="http", auth="user", methods=["GET"], website=True, csrf=False)
    def submit_product(self, id):
        product = request.env["product.template"].browse(id)
        if not product.exists():
            raise http.NotFound()

        product.action_submit()

        return request.redirect("/my/writer_products")

    @http.route(["/my/writer_targets", "/my/writer_targets/page/<int:page>"], type="http", auth="user", website=True)
    def get_writer_targets(self, page=1, search=None, search_in="all"):
        domain = writer_target.get_search_domain(search_in, search)
        if not domain:
            search = None
            search_in = "all"

        writer_target_obj = request.env["writer.target"]

        writer_target_count = writer_target_obj.search_count(domain)

        pager = portal_pager(
            url="/my/writer_targets",
            url_args={
                "search_in": search_in,
                "search": search,
            },
            total=writer_target_count,
            page=page,
            step=self._items_per_page,
        )

        writer_targets = writer_target_obj.search(domain, limit=self._items_per_page, offset=pager["offset"])

        request.session["my_writer_targets_history"] = writer_targets.ids[:100]

        return request.render(
            "writer.portal_my_writer_targets",
            {
                "page_name": "Writer Target Report",
                "pager": pager,
                "default_url": "/my/writer_targets",
                "searchbar_inputs": writer_target.get_searchbar_inputs(),
                "search": search,
                "search_in": search_in,
                "writer_targets": writer_targets,
            },
        )

    @http.route(["/my/writer_targets/export"], type="http", auth="user", methods=["POST"], website=True, csrf=False)
    def export_writer_targets(self, **kw):
        ids = []

        selected_ids = request.httprequest.form.get("export_writer_target_ids", "")
        if selected_ids:
            ids = [int(id) for id in selected_ids.split(",")]

        if not ids:
            ids = request.session["my_writer_targets_history"]

        data = {
            "import_compat": False,
            "model": "writer.target",
            "ids": ids,
            "fields": writer_target.prepare_columns_epxort(),
            "domain": [],
            "groupby": [],
            "context": request.context,
        }

        response = ExcelExport().base(json.dumps(data))

        filename = f"writer_targets_{datetime.now().date()}.xlsx"
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"

        return response

    @http.route(["/my/writer_commission_lines", "/my/writer_commission_lines/page/<int:page>"], type="http", auth="user", website=True)
    def commission_lines(self, page=1, search=None, search_in="all", groupby="none"):
        domain = writer_commission.get_search_domain(search_in, search)
        if not domain:
            search = None
            search_in = "all"

        writer_commission_line_obj = request.env["writer.commission.line"]

        writer_commissions_count = writer_commission_line_obj.search_count(domain)

        groupby_mapping = writer_commission.get_groupby_mapping()
        group = groupby_mapping.get(groupby)
        if not group:
            groupby = "none"

        pager = portal_pager(
            url="/my/writer_commission_lines",
            url_args={
                "groupby": groupby,
                "search_in": search_in,
                "search": search,
            },
            total=writer_commissions_count,
            page=page,
            step=self._items_per_page,
        )

        writer_commission_lines = writer_commission_line_obj.search(domain, limit=self._items_per_page, offset=pager["offset"])

        request.session["my_writer_commission_lines_history"] = writer_commission_lines.ids[:100]

        if group:
            grouped_commission_lines = [writer_commission_line_obj.concat(*g) for k, g in groupbyelem(writer_commission_lines, itemgetter(group))]
        else:
            grouped_commission_lines = writer_commission_lines

        return request.render(
            "writer.portal_my_writer_commission_lines",
            {
                "page_name": "Writer Commission Report",
                "pager": pager,
                "default_url": "/my/writer_commission_lines",
                "searchbar_groupby": writer_commission.get_searchbar_groupby(),
                "searchbar_inputs": writer_commission.get_searchbar_inputs(),
                "search": search,
                "search_in": search_in,
                "groupby": groupby,
                "grouped_commission_lines": grouped_commission_lines,
            },
        )

    @http.route(["/my/writer_commission_lines/export"], type="http", auth="user", methods=["POST"], website=True, csrf=False)
    def export_commission_lines(self, groupby=False):
        ids = []

        selected_ids = request.httprequest.form.get("export_writer_commission_line_ids", "")
        if selected_ids:
            ids = [int(id) for id in selected_ids.split(",")]

        if not ids:
            ids = request.session["my_writer_commission_lines_history"]

        groupby = writer_commission.get_groupby_mapping().get(groupby)

        data = {
            "import_compat": False,
            "model": "writer.commission.line",
            "ids": ids,
            "fields": writer_commission.prepare_columns_epxort(),
            "domain": [],
            "groupby": groupby and [groupby] or [],
            "context": request.context,
        }

        response = ExcelExport().base(json.dumps(data))

        filename = f"commission_lines_{datetime.now().date()}.xlsx"
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"

        return response

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)

        if "writer_products_count" in counters:
            values["writer_products_count"] = (
                request.env["product.template"].search_count([]) if request.env["product.template"].check_access_rights("read", raise_exception=False) else 0
            )

        if "writer_commissions_count" in counters:
            values["writer_commissions_count"] = (
                request.env["writer.commission.line"].search_count([]) if request.env["writer.commission.line"].check_access_rights("read", raise_exception=False) else 0
            )

        if "writer_targets_count" in counters:
            values["writer_targets_count"] = request.env["writer.target"].search_count([]) if request.env["writer.target"].check_access_rights("read", raise_exception=False) else 0

        return values
