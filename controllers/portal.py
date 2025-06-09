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

    # @staticmethod
    # def _action_update_html_field(record, field_name, value, lang_code_ar, lang_code_en):
    #     field = record._fields[field_name]
    #     translations = field._get_stored_translations(record)
    #     from_lang_value = translations.get(lang_code_ar)
    #     empty_translate_arabic = False
    #     if not from_lang_value:
    #         empty_translate_arabic = True
    #         from_lang_value = translations[lang_code_en]
    #
    #     translation_dictionary = field.get_translation_dictionary(from_lang_value, translations)
    #
    #     new_arabic_terms = field.get_trans_terms(value)
    #     new_translations = defaultdict(dict)
    #     next_term = 0
    #     for from_lang_term, to_lang_terms in translation_dictionary.items():
    #         for lang, to_lang_term in to_lang_terms.items():
    #             if lang == lang_code_ar:
    #                 if next_term >= len(new_arabic_terms):
    #                     new_translations[lang][from_lang_term] = ""
    #                 else:
    #                     new_translations[lang][from_lang_term] = new_arabic_terms[next_term]
    #                     next_term += 1
    #             elif empty_translate_arabic:
    #                 new_translations[lang_code_ar][from_lang_term] = new_arabic_terms[next_term]
    #                 next_term += 1
    #
    #     record.update_field_translations(field_name, new_translations)
    #
    #     return True

    # @http.route(["/my/writer_product_categories/edit/<int:id>"], type="http", auth="user", methods=["GET", "POST"], website=True, csrf=False)
    # def edit_category(self, id):
    #     if not request.env.user.employee_id.is_writer:
    #         return request.redirect("/my")
    #
    #     category_ids = (
    #         request.env["product.template"]
    #         .search(
    #             [
    #                 ("writer_id", "=", request.env.user.employee_id.id),
    #                 ("state", "=", "draft"),
    #             ]
    #         )
    #         .mapped("categ_id")
    #         .ids
    #     )
    #     product_category = request.env["product.category"].search(
    #         [
    #             ("id", "=", id),
    #             ("id", "in", category_ids),
    #         ],
    #         limit=1,
    #     )
    #     if not product_category:
    #         return request.redirect("/my")
    #
    #     lang_code_en = request.env.ref("base.lang_en").code
    #     lang_ar = request.env.ref("base.lang_ar")
    #     lang_code_ar = False
    #     if lang_ar.active:
    #         lang_code_ar = lang_ar.code
    #
    #     if request.httprequest.method == "GET":
    #         return request.render(
    #             "writer.portal_my_writer_product_category_edit",
    #             {
    #                 "page_name": "Writer Product Category",
    #                 "product_category": product_category,
    #                 "lang_code_en": lang_code_en,
    #                 "lang_code_ar": lang_code_ar,
    #             },
    #         )
    #
    #     data = request.httprequest.form
    #     vals = {
    #         "name": data["name"],
    #         "description": data["description"],
    #         "meta_description": data["meta_description"],
    #         "seo_title": data["seo_title"],
    #         "seo_description": data["seo_description"],
    #     }
    #
    #     edit_delete_image = data["edit_delete_image"]
    #     if edit_delete_image == "1":
    #         image = request.httprequest.files.getlist("image")
    #         vals.update({"image_1920": base64.b64encode(image[0].read())})
    #     elif edit_delete_image == "2":
    #         vals.update({"image_1920": False})
    #
    #     product_category.with_context(lang=lang_code_en).write(vals)
    #
    #     if lang_code_ar:
    #         product_category.with_context(lang=lang_code_ar).write(
    #             {
    #                 "name": data["name_arabic"],
    #                 "description": data["description"],
    #                 "meta_description": data["meta_description"],
    #                 "seo_title": data["seo_title_arabic"],
    #                 "seo_description": data["seo_description_arabic"],
    #             }
    #         )
    #
    #         self._action_update_html_field(product_category, "description", data["description_arabic"], lang_code_ar, lang_code_en)
    #         self._action_update_html_field(product_category, "meta_description", data["meta_description_arabic"], lang_code_ar, lang_code_en)
    #
    #     # add or edit or delete faqs
    #     add_faqs = {}
    #     edit_faqs = {}
    #     delete_faqs = data["delete_faqs"]
    #     delete_faqs = delete_faqs and eval(delete_faqs) or []
    #     delete_faqs = [int(delete_faq) for delete_faq in delete_faqs]
    #
    #     for key, val in data.items():
    #         if "add_faq" in key or "edit_faq" in key:
    #             key_list = key.split("_")
    #             field_key = "_".join(key_list[2 : len(key_list) - 1])
    #             faq_id = key_list[-1]
    #
    #             if key_list[0] == "add":
    #                 if faq_id not in add_faqs:
    #                     add_faqs.update({key_list[-1]: {}})
    #
    #                 add_faqs[faq_id].update({field_key: val})
    #             else:
    #                 if faq_id not in edit_faqs:
    #                     edit_faqs.update({key_list[-1]: {}})
    #
    #                 edit_faqs[faq_id].update({field_key: val})
    #
    #     if delete_faqs:
    #         faqs = product_category.faq_ids.filtered(lambda f: f.id in delete_faqs)
    #         if faqs:
    #             faqs.unlink()
    #
    #     product_category_faq_obj = request.env["product.category.faq"]
    #     for faq_id, faq_vals in edit_faqs.items():
    #         faq = product_category_faq_obj.browse(int(faq_id))
    #         if faq.exists():
    #             faq.write(
    #                 {
    #                     "quotation": faq_vals["quotation"],
    #                     "answer": faq_vals["answer"],
    #                 }
    #             )
    #
    #             if lang_code_ar:
    #                 faq.with_context(lang=lang_code_ar).write(
    #                     {
    #                         "quotation": faq_vals["quotation_arabic"],
    #                         "answer": faq_vals["answer_arabic"],
    #                     }
    #                 )
    #
    #     for faq_id, faq_vals in add_faqs.items():
    #         faq = product_category_faq_obj.create({"quotation": faq_vals["quotation"], "answer": faq_vals["answer"], "product_category_id": product_category.id})
    #
    #         if lang_code_ar:
    #             faq.with_context(lang=lang_code_ar).write(
    #                 {
    #                     "quotation": faq_vals["quotation_arabic"],
    #                     "answer": faq_vals["answer_arabic"],
    #                 }
    #             )
    #
    #     return request.redirect("/my")

    # @http.route(["/my/writer_product_brands/edit/<int:id>"], type="http", auth="user", methods=["GET", "POST"], website=True, csrf=False)
    # def edit_brand(self, id):
    #     if not request.env.user.employee_id.is_writer:
    #         return request.redirect("/my")
    #
    #     brand_ids = (
    #         request.env["product.template"]
    #         .search(
    #             [
    #                 ("writer_id", "=", request.env.user.employee_id.id),
    #                 ("state", "=", "draft"),
    #             ]
    #         )
    #         .mapped("brand_id")
    #         .ids
    #     )
    #     product_brand = request.env["product.brand"].search(
    #         [
    #             ("id", "=", id),
    #             ("id", "in", brand_ids),
    #         ],
    #         limit=1,
    #     )
    #     if not product_brand:
    #         return request.redirect("/my")
    #
    #     lang_code_en = request.env.ref("base.lang_en").code
    #     lang_ar = request.env.ref("base.lang_ar")
    #     lang_code_ar = False
    #     if lang_ar.active:
    #         lang_code_ar = lang_ar.code
    #
    #     if request.httprequest.method == "GET":
    #         return request.render(
    #             "writer.portal_my_writer_product_brand_edit",
    #             {"page_name": "Writer Product Brand", "product_brand": product_brand, "lang_code_en": lang_code_en, "lang_code_ar": lang_code_ar},
    #         )
    #
    #     data = request.httprequest.form
    #
    #     vals = {"name": data["name"], "description": data["description"], "seo_title": data["seo_title"], "seo_description": data["seo_description"]}
    #
    #     edit_delete_image = data["edit_delete_image"]
    #     if edit_delete_image == "1":
    #         image = request.httprequest.files.getlist("image")
    #         vals.update({"image_1920": base64.b64encode(image[0].read())})
    #     elif edit_delete_image == "2":
    #         vals.update({"image_1920": False})
    #
    #     product_brand.with_context(lang=lang_code_en).write(vals)
    #
    #     if lang_code_ar:
    #         product_brand.with_context(lang=lang_code_ar).write(
    #             {"name": data["name_arabic"], "description": data["description"], "seo_title": data["seo_title_arabic"], "seo_description": data["seo_description_arabic"]}
    #         )
    #
    #         # update arabic description
    #         self._action_update_html_field(product_brand, "description", data["description_arabic"], lang_code_ar, lang_code_en)
    #
    #     return request.redirect("/my/writer_product_brands")

    # @http.route(["/my/writer_product_tags/edit/<int:id>"], type="http", auth="user", methods=["GET", "POST"], website=True, csrf=False)
    # def edit_tag(self, id):
    #     if not request.env.user.employee_id.is_writer:
    #         return request.redirect("/my")
    #
    #     tag_ids = (
    #         request.env["product.template"]
    #         .search(
    #             [
    #                 ("writer_id", "=", request.env.user.employee_id.id),
    #                 ("state", "=", "draft"),
    #             ]
    #         )
    #         .mapped("product_tag_ids")
    #         .ids
    #     )
    #     product_tag = request.env["product.tag"].search(
    #         [
    #             ("id", "=", id),
    #             ("id", "in", tag_ids),
    #         ],
    #         limit=1,
    #     )
    #     if not product_tag:
    #         return request.redirect("/my")
    #
    #     lang_code_en = request.env.ref("base.lang_en").code
    #     lang_ar = request.env.ref("base.lang_ar")
    #     lang_code_ar = False
    #     if lang_ar.active:
    #         lang_code_ar = lang_ar.code
    #
    #     if request.httprequest.method == "GET":
    #         return request.render(
    #             "writer.portal_my_writer_product_tag_edit",
    #             {"page_name": "Writer Product Tag", "product_tag": product_tag, "lang_code_en": lang_code_en, "lang_code_ar": lang_code_ar},
    #         )
    #
    #     data = request.httprequest.form
    #     product_tag.with_context(lang=lang_code_en).write(
    #         {
    #             "name": data["name"],
    #             "description": data["description"],
    #             "seo_title": data["seo_title"],
    #             "seo_description": data["seo_description"],
    #         }
    #     )
    #
    #     if lang_code_ar:
    #         product_tag.with_context(lang=lang_code_ar).write(
    #             {
    #                 "name": data["name_arabic"],
    #                 "description": data["description"],
    #                 "seo_title": data["seo_title_arabic"],
    #                 "seo_description": data["seo_description_arabic"],
    #             }
    #         )
    #
    #         # update arabic description
    #         self._action_update_html_field(product_tag, "description", data["description_arabic"], lang_code_ar, lang_code_en)
    #
    #     # add or edit or delete faqs
    #     add_faqs = {}
    #     edit_faqs = {}
    #     delete_faqs = data["delete_faqs"]
    #     delete_faqs = delete_faqs and eval(delete_faqs) or []
    #     delete_faqs = [int(delete_faq) for delete_faq in delete_faqs]
    #
    #     for key, val in data.items():
    #         if "add_faq" in key or "edit_faq" in key:
    #             key_list = key.split("_")
    #             field_key = "_".join(key_list[2 : len(key_list) - 1])
    #             faq_id = key_list[-1]
    #
    #             if key_list[0] == "add":
    #                 if faq_id not in add_faqs:
    #                     add_faqs.update({key_list[-1]: {}})
    #
    #                 add_faqs[faq_id].update({field_key: val})
    #             else:
    #                 if faq_id not in edit_faqs:
    #                     edit_faqs.update({key_list[-1]: {}})
    #
    #                 edit_faqs[faq_id].update({field_key: val})
    #
    #     if delete_faqs:
    #         faqs = product_tag.faq_ids.filtered(lambda f: f.id in delete_faqs)
    #         if faqs:
    #             faqs.unlink()
    #
    #     product_tag_faq_obj = request.env["product.tag.faq"]
    #     for faq_id, faq_vals in edit_faqs.items():
    #         faq = product_tag_faq_obj.browse(int(faq_id))
    #         if faq.exists():
    #             faq.write(
    #                 {
    #                     "quotation": faq_vals["quotation"],
    #                     "answer": faq_vals["answer"],
    #                 }
    #             )
    #
    #             if lang_code_ar:
    #                 faq.with_context(lang=lang_code_ar).write(
    #                     {
    #                         "quotation": faq_vals["quotation_arabic"],
    #                         "answer": faq_vals["answer_arabic"],
    #                     }
    #                 )
    #
    #     for faq_id, faq_vals in add_faqs.items():
    #         faq = product_tag_faq_obj.create({"quotation": faq_vals["quotation"], "answer": faq_vals["answer"], "product_tag_id": product_tag.id})
    #
    #         if lang_code_ar:
    #             faq.with_context(lang=lang_code_ar).write(
    #                 {
    #                     "quotation": faq_vals["quotation_arabic"],
    #                     "answer": faq_vals["answer_arabic"],
    #                 }
    #             )
    #
    #     return request.redirect("/my")
