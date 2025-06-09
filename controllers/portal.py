# -*- coding: utf-8 -*-

import base64
import json
from collections import defaultdict, OrderedDict
from operator import itemgetter

from odoo import http, _
from odoo.addons.base.models.ir_qweb import keep_query
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.osv.expression import OR
from odoo.tools import groupby as groupbyelem


class WriterPortal(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)

        employee = request.env.user.employee_id

        if "writer_products_count" in counters:
            writer_products_count = (
                    request.env["product.template"].check_access_rights("read", raise_exception=False) and
                    request.env["product.template"].search_count([("writer_id", "=", employee.id)]) or 0)
            values["writer_products_count"] = writer_products_count

        if "writer_product_brands_count" in counters:
            writer_product_brands_count = (
                    request.env["product.template"].check_access_rights("read", raise_exception=False) and
                    len(request.env["product.template"].search([("writer_id", "=", employee.id)]).mapped(
                        "brand_id")) or 0)
            values["writer_product_brands_count"] = writer_product_brands_count

        if "writer_product_tags_count" in counters:
            writer_product_tags_count = (
                    request.env["product.template"].check_access_rights("read", raise_exception=False) and
                    len(request.env["product.template"].search([("writer_id", "=", employee.id)]).mapped(
                        "product_tag_ids")) or 0)
            values["writer_product_tags_count"] = writer_product_tags_count

        if "writer_product_categories_count" in counters:
            writer_product_categories_count = (
                    request.env["product.category"].check_access_rights("read", raise_exception=False) and
                    request.env["product.category"].search_count([("writer_id", "=", employee.id)]) or 0)
            values["writer_product_categories_count"] = writer_product_categories_count

        if "writer_commissions_count" in counters:
            writer_commissions_count = (
                    request.env["writer.commission.line"].check_access_rights("read", raise_exception=False) and
                    request.env["writer.commission.line"].search_count([("writer_id", "=", employee.id)]) or 0)
            values["writer_commissions_count"] = writer_commissions_count

        if "writer_target_lines_count" in counters:
            writer_target_lines_count = (
                    request.env["writer.target.line"].check_access_rights("read", raise_exception=False) and
                    request.env["writer.target.line"].search_count([("writer_id", "=", employee.id)]) or 0)
            values["writer_target_lines_count"] = writer_target_lines_count

        return values

    def _get_writer_products_searchbar_groupby(self):
        values = {
            "none": {"input": "none", "label": _("None"), "order": 1},
            "category": {"input": "category", "label": _("Category"), "order": 2},
            "brand": {"input": "brand", "label": _("Brand"), "order": 3},
            "state": {"input": "state", "label": _("Status"), "order": 4}
        }

        return dict(sorted(values.items(), key=lambda item: item[1]["order"]))

    def _get_writer_products_get_groupby_mapping(self):
        return {
            "category": "categ_id",
            "brand": "brand_id",
            "state": "state"
        }

    def _get_writer_products_searchbar_inputs(self):
        values = {
            "all": {"input": "all", "label": _("Search in All"), "order": 1},
            "name": {"input": "name", "label": _("Search in Name"), "order": 2},
            "internal_reference": {"input": "internal_reference", "label": _("Search in Internal Reference"),
                                   "order": 3},
            "brand": {"input": "brand", "label": _("Search in Brand"), "order": 4},
            "tags": {"input": "tags", "label": _("Search in Product Tags"), "order": 5}
        }

        return dict(sorted(values.items(), key=lambda item: item[1]["order"]))

    def _get_writer_products_search_domain(self, search_in, search):
        search_domain = []

        if search_in in ("name", "all"):
            search_domain.append([("name", "ilike", search)])

        if search_in in ("internal_reference", "all"):
            search_domain.append([("default_code", "ilike", search)])

        if search_in in ("brand", "all"):
            search_domain.append([("brand_id", "ilike", search)])

        if search_in in ("tags", "all"):
            search_domain.append([("product_tag_ids", "ilike", search)])

        return OR(search_domain)

    @http.route(["/my/writer_products", "/my/writer_products/page/<int:page>"], type="http",
                auth="user", website=True)
    def portal_my_writer_products(self, page=1, sortby=None, filterby=None, search=None, search_in="all",
                                  groupby="none"):
        if not request.env.user.employee_id.is_writer:
            return request.redirect("/my")

        values = self._prepare_portal_layout_values()
        searchbar_groupby = self._get_writer_products_searchbar_groupby()
        searchbar_inputs = self._get_writer_products_searchbar_inputs()
        domain = [("writer_id", "=", request.env.user.employee_id.id)]

        # search
        if search and search_in:
            domain += self._get_writer_products_search_domain(search_in, search)

        product_template_obj = request.env["product.template"]

        # writer products count
        writer_products_count = product_template_obj.search_count(domain)

        # pager
        pager = portal_pager(
            url="/my/writer_products",
            url_args={"sortby": sortby, "groupby": groupby, "search_in": search_in, "search": search,
                      "filterby": filterby},
            total=writer_products_count,
            page=page,
            step=self._items_per_page)

        writer_products = product_template_obj.search(domain, limit=self._items_per_page, offset=pager["offset"])

        request.session["my_writer_products_history"] = writer_products.ids[:100]

        groupby_mapping = self._get_writer_products_get_groupby_mapping()
        group = groupby_mapping.get(groupby)

        if group:
            grouped_products = [product_template_obj.concat(*g) for k, g in
                                groupbyelem(writer_products, itemgetter(group))]
        else:
            grouped_products = writer_products

        values.update({
            "page_name": "Writer Product",
            "pager": pager,
            "default_url": "/my/writer_products",
            "searchbar_groupby": searchbar_groupby,
            "searchbar_inputs": searchbar_inputs,
            "sortby": sortby,
            "filterby": filterby,
            "search": search,
            "search_in": search_in,
            "groupby": groupby,
            "grouped_products": grouped_products
        })

        return request.render("writer.portal_my_writer_products", values)

    def action_portal_writer_update_html_field(self, record, field_name, value, lang_code_ar, lang_code_en):
        field = record._fields[field_name]
        translations = field._get_stored_translations(record)
        from_lang_value = translations.get(lang_code_ar)
        empty_translate_arabic = False
        if not from_lang_value:
            empty_translate_arabic = True
            from_lang_value = translations[lang_code_en]

        translation_dictionary = field.get_translation_dictionary(from_lang_value, translations)

        new_arabic_terms = field.get_trans_terms(value)
        new_translations = defaultdict(dict)
        next_term = 0
        for from_lang_term, to_lang_terms in translation_dictionary.items():
            for lang, to_lang_term in to_lang_terms.items():
                if lang == lang_code_ar:
                    if next_term >= len(new_arabic_terms):
                        new_translations[lang][from_lang_term] = ""
                    else:
                        new_translations[lang][from_lang_term] = new_arabic_terms[next_term]
                        next_term += 1
                elif empty_translate_arabic:
                    new_translations[lang_code_ar][from_lang_term] = new_arabic_terms[next_term]
                    next_term += 1

        record.update_field_translations(field_name, new_translations)

        return True

    @http.route(["/my/writer_products/edit/<int:id>"], type="http", auth="user", methods=["GET", "POST"], website=True,
                csrf=False)
    def portal_edit_writer_product(self, id, access_token=None, **kw):
        if not request.env.user.employee_id.is_writer:
            return request.redirect("/my")

        product = request.env["product.template"].search([("id", "=", id), ("state", "=", "draft")], limit=1)
        if not product:
            return request.redirect("/my/writer_products")

        lang_code_en = request.env.ref("base.lang_en").code
        lang_ar = request.env.ref("base.lang_ar")
        lang_code_ar = False
        if lang_ar.active:
            lang_code_ar = lang_ar.code

        if request.httprequest.method == "GET":
            return request.render("writer.portal_my_writer_product_edit", {
                "page_name": "Writer Product",
                "product": product,
                "lang_code_en": lang_code_en,
                "lang_code_ar": lang_code_ar
            })

        data = request.httprequest.form

        brand_id = data.get("brand_id", False)
        if brand_id:
            brand_id = int(brand_id)

        product_tag_ids = []
        for product_tag_id in data.getlist("product_tag_ids"):
            product_tag_ids.append(int(product_tag_id))

        vals = {
            "name": data["name"],
            "description": data["description"],
            "description_arabic": data["description_arabic"],
            "seo_title": data["seo_title"],
            "seo_description": data["seo_description"],
            "brand_id": brand_id,
            "product_tag_ids": [(6, 0, product_tag_ids)]
        }

        update_product_image_types = data["update_product_image_types"]
        update_product_image_types = update_product_image_types and eval(update_product_image_types) or {}
        product_image_obj = request.env["product.image"]
        # edit product images
        for key, image in request.httprequest.files.items():
            key_list = key.split("_")
            if key_list[0] == "edit":
                if key_list[1] == "product":
                    product.write({"image_1920": base64.b64encode(image.read())})
                else:
                    product_image_id = key_list[2]
                    product_image = product_image_obj.browse(int(product_image_id))
                    if product_image.exists():
                        image_vals = {"image_1920": base64.b64encode(image.read())}
                        if product_image_id in update_product_image_types:
                            image_vals.update({"type": update_product_image_types[product_image_id]})
                            del update_product_image_types[product_image_id]

                        product_image.write(image_vals)

        # delete product images
        delete_image_ids = data["delete_image_ids"]
        delete_image_ids = delete_image_ids and eval(delete_image_ids) or []
        for delete_image in delete_image_ids:
            if delete_image["model"] == "product.template":
                product.write({"image_1920": False})
            else:
                product_image = product_image_obj.browse(int(delete_image["id"]))
                if product_image.exists():
                    product_image.unlink()

        # add product images
        for key, image in request.httprequest.files.items():
            key_list = key.split("_")
            if key_list[0] == "add":
                image_type = "gallery"
                if key in update_product_image_types:
                    image_type = update_product_image_types[key]
                    del update_product_image_types[key]

                product_image_obj.create({
                    "product_tmpl_id": product.id,
                    "name": image.filename,
                    "image_1920": base64.b64encode(image.read()),
                    "type": image_type
                })


        for product_image_id, image_type in update_product_image_types.items():
            product_image = product_image_obj.browse(int(product_image_id))
            if product_image.exists():
                product_image.write({"type": image_type})

        product.with_context(lang=lang_code_en).write(vals)

        if lang_code_ar:
            vals = {
                "name": data["name_arabic"],
                "seo_title": data["seo_title_arabic"],
                "seo_description": data["seo_description_arabic"]
            }

            product.with_context(lang=lang_code_ar).write(vals)

        if data.get("submit_option", False):
            product.action_submit()

        return request.redirect("/my/writer_products")

    @http.route(["/my/writer_products/submit/<int:id>"], type="http", auth="user", methods=["GET"], website=True,
                csrf=False)
    def portal_submit_writer_product(self, id, access_token=None, **kw):
        if not request.env.user.employee_id.is_writer:
            return request.redirect("/my")

        product = request.env["product.template"].search([("id", "=", id), ("state", "=", "draft")], limit=1)
        if not product:
            return request.redirect("/my/writer_products")

        product.action_submit()

        return request.redirect("/my/writer_products")

    def _get_writer_product_categories_searchbar_groupby(self):
        values = {
            "none": {"input": "none", "label": _("None"), "order": 1},
            "state": {"input": "state", "label": _("Status"), "order": 2}
        }

        return dict(sorted(values.items(), key=lambda item: item[1]["order"]))

    def _get_writer_product_categories_get_groupby_mapping(self):
        return {
            "state": "state"
        }

    def _get_writer_product_categories_searchbar_inputs(self):
        values = {
            "all": {"input": "all", "label": _("Search in All"), "order": 1},
            "name": {"input": "all", "label": _("Search in Name"), "order": 1}
        }

        return dict(sorted(values.items(), key=lambda item: item[1]["order"]))

    def _get_writer_product_categories_search_domain(self, search_in, search):
        search_domain = []

        if search_in in ("name", "all"):
            search_domain.append([("name", "ilike", search)])

        return OR(search_domain)

    @http.route(["/my/writer_product_categories", "/my/writer_product_categories/page/<int:page>"], type="http",
                auth="user", website=True)
    def portal_my_writer_product_categories(self, page=1, sortby=None, filterby=None, search=None, search_in="all",
                                            groupby="none"):
        if not request.env.user.employee_id.is_writer:
            return request.redirect("/my")

        values = self._prepare_portal_layout_values()
        searchbar_groupby = self._get_writer_product_categories_searchbar_groupby()
        searchbar_inputs = self._get_writer_product_categories_searchbar_inputs()
        domain = [("writer_id", "=", request.env.user.employee_id.id)]

        # search
        if search and search_in:
            domain += self._get_writer_product_categories_search_domain(search_in, search)

        product_category_obj = request.env["product.category"]

        # writer product categories count
        writer_product_categories_count = product_category_obj.search_count(domain)

        # pager
        pager = portal_pager(
            url="/my/writer_product_categories",
            url_args={"sortby": sortby, "groupby": groupby, "search_in": search_in, "search": search,
                      "filterby": filterby},
            total=writer_product_categories_count,
            page=page,
            step=self._items_per_page)

        writer_product_categories = product_category_obj.search(domain, limit=self._items_per_page,
                                                                offset=pager["offset"])

        request.session["my_writer_products_history"] = writer_product_categories.ids[:100]

        groupby_mapping = self._get_writer_products_get_groupby_mapping()
        group = groupby_mapping.get(groupby)

        if group:
            grouped_product_categories = [product_category_obj.concat(*g) for k, g in
                                          groupbyelem(writer_product_categories, itemgetter(group))]
        else:
            grouped_product_categories = writer_product_categories

        values.update({
            "page_name": "Writer Product Category",
            "pager": pager,
            "default_url": "/my/writer_product_categories",
            "searchbar_groupby": searchbar_groupby,
            "searchbar_inputs": searchbar_inputs,
            "sortby": sortby,
            "filterby": filterby,
            "search": search,
            "search_in": search_in,
            "groupby": groupby,
            "grouped_product_categories": grouped_product_categories
        })

        return request.render("writer.portal_my_writer_product_categories", values)

    @http.route(["/my/writer_product_categories/edit/<int:id>"], type="http", auth="user", methods=["GET", "POST"],
                website=True, csrf=False)
    def portal_edit_writer_product_category(self, id, access_token=None, **kw):
        if not request.env.user.employee_id.is_writer:
            return request.redirect("/my")

        product_category = request.env["product.category"].search([("id", "=", id), ("state", "=", "draft")],
                                                                  limit=1)
        if not product_category:
            return request.redirect("/my/writer_product_categories")

        lang_code_en = request.env.ref("base.lang_en").code
        lang_ar = request.env.ref("base.lang_ar")
        lang_code_ar = False
        if lang_ar.active:
            lang_code_ar = lang_ar.code

        if request.httprequest.method == "GET":
            return request.render("writer.portal_my_writer_product_category_edit", {
                "page_name": "Writer Product Category",
                "product_category": product_category,
                "lang_code_en": lang_code_en,
                "lang_code_ar": lang_code_ar
            })

        data = request.httprequest.form
        vals = {
            "name": data["name"],
            "description": data["description"],
            "meta_description": data["meta_description"],
            "seo_title": data["seo_title"],
            "seo_description": data["seo_description"]
        }

        edit_delete_image = data["edit_delete_image"]
        if edit_delete_image == "1":
            image = request.httprequest.files.getlist("image")
            vals.update({"image_1920": base64.b64encode(image[0].read())})
        elif edit_delete_image == "2":
            vals.update({"image_1920": False})

        product_category.with_context(lang=lang_code_en).write(vals)

        if lang_code_ar:
            product_category.with_context(lang=lang_code_ar).write({
                "name": data["name_arabic"],
                "description": data["description"],
                "meta_description": data["meta_description"],
                "seo_title": data["seo_title_arabic"],
                "seo_description": data["seo_description_arabic"]
            })

            # update arabic description,meta description terms
            self.action_portal_writer_update_html_field(product_category, "description", data["description_arabic"],
                                                        lang_code_ar, lang_code_en)
            self.action_portal_writer_update_html_field(product_category, "meta_description",
                                                        data["meta_description_arabic"], lang_code_ar, lang_code_en)

        # add or edit or delete faqs
        add_faqs = {}
        edit_faqs = {}
        delete_faqs = data["delete_faqs"]
        delete_faqs = delete_faqs and eval(delete_faqs) or []
        delete_faqs = [int(delete_faq) for delete_faq in delete_faqs]

        for key, val in data.items():
            if "add_faq" in key or "edit_faq" in key:
                key_list = key.split("_")
                field_key = "_".join(key_list[2:len(key_list) - 1])
                faq_id = key_list[-1]

                if key_list[0] == "add":
                    if faq_id not in add_faqs:
                        add_faqs.update({key_list[-1]: {}})

                    add_faqs[faq_id].update({field_key: val})
                else:
                    if faq_id not in edit_faqs:
                        edit_faqs.update({key_list[-1]: {}})

                    edit_faqs[faq_id].update({field_key: val})

        if delete_faqs:
            faqs = product_category.faq_ids.filtered(lambda f: f.id in delete_faqs)
            if faqs:
                faqs.unlink()

        product_category_faq_obj = request.env["product.category.faq"]
        for faq_id, faq_vals in edit_faqs.items():
            faq = product_category_faq_obj.browse(int(faq_id))
            if faq.exists():
                faq.write({
                    "quotation": faq_vals["quotation"],
                    "answer": faq_vals["answer"],
                })

                if lang_code_ar:
                    faq.with_context(lang=lang_code_ar).write({
                        "quotation": faq_vals["quotation_arabic"],
                        "answer": faq_vals["answer_arabic"],
                    })

        for faq_id, faq_vals in add_faqs.items():
            faq = product_category_faq_obj.create({
                "quotation": faq_vals["quotation"],
                "answer": faq_vals["answer"],
                "product_category_id": product_category.id
            })

            if lang_code_ar:
                faq.with_context(lang=lang_code_ar).write({
                    "quotation": faq_vals["quotation_arabic"],
                    "answer": faq_vals["answer_arabic"],
                })

        if data.get("submit_option", False):
            product_category.action_submit()

        return request.redirect("/my/writer_product_categories")

    @http.route(["/my/writer_product_categories/submit/<int:id>"], type="http", auth="user", methods=["GET"],
                website=True, csrf=False)
    def portal_submit_writer_product_category(self, id, access_token=None, **kw):
        if not request.env.user.employee_id.is_writer:
            return request.redirect("/my")

        product_category = request.env["product.category"].search([("id", "=", id), ("state", "=", "draft")],
                                                                  limit=1)
        if not product_category:
            return request.redirect("/my/writer_product_categories")

        product_category.action_submit()

        return request.redirect("/my/writer_product_categories")

    def _get_writer_commissions_searchbar_groupby(self):
        values = {
            "none": {"input": "none", "label": _("None"), "order": 1},
            "date": {"input": "date", "label": _("Date"), "order": 2},
            "type": {"input": "type", "label": _("Type"), "order": 3},
            "product": {"input": "product", "label": _("Product"), "order": 4},
            "product_category": {"input": "product_category", "label": _("Product Category"), "order": 5},
            "state": {"input": "state", "label": _("Status"), "order": 6}
        }

        return dict(sorted(values.items(), key=lambda item: item[1]["order"]))

    def _get_writer_commissions_get_groupby_mapping(self):
        return {
            "state": "state",
            "date": "date",
            "type": "type",
            "product": "product_template_id",
            "product_category": "product_category_id"
        }

    def _get_writer_commissions_searchbar_inputs(self):
        values = {
            "all": {"input": "all", "label": _("Search in All"), "order": 1},
            "date": {"input": "date", "label": _("Search in Date"), "order": 2}
        }

        return dict(sorted(values.items(), key=lambda item: item[1]["order"]))

    def _get_writer_commissions_search_domain(self, search_in, search):
        search_domain = []

        if search_in in ("date", "all"):
            search_domain.append([("date", "ilike", search)])

        return OR(search_domain)

    @http.route(["/my/writer_commission_lines", "/my/writer_commission_lines/page/<int:page>"], type="http",
                auth="user", website=True)
    def portal_my_writer_commissions(self, page=1, sortby=None, filterby=None, search=None, search_in="all",
                                     groupby="none"):
        if not request.env.user.employee_id.is_writer:
            return request.redirect("/my")

        values = self._prepare_portal_layout_values()
        searchbar_groupby = self._get_writer_commissions_searchbar_groupby()
        searchbar_inputs = self._get_writer_commissions_searchbar_inputs()
        domain = [("writer_id", "=", request.env.user.employee_id.id)]

        # search
        if search and search_in:
            domain += self._get_writer_commissions_search_domain(search_in, search)

        writer_commission_line_obj = request.env["writer.commission.line"]

        # writer commissions count
        writer_commissions_count = writer_commission_line_obj.search_count(domain)

        # pager
        pager = portal_pager(
            url="/my/writer_commission_lines",
            url_args={"sortby": sortby, "groupby": groupby, "search_in": search_in, "search": search,
                      "filterby": filterby},
            total=writer_commissions_count,
            page=page,
            step=self._items_per_page)

        writer_commission_lines = writer_commission_line_obj.search(domain, limit=self._items_per_page,
                                                                    offset=pager["offset"])

        request.session["my_writer_commission_lines_history"] = writer_commission_lines.ids[:100]

        groupby_mapping = self._get_writer_commissions_get_groupby_mapping()
        group = groupby_mapping.get(groupby)

        if group:
            grouped_commission_lines = [writer_commission_line_obj.concat(*g)
                                        for k, g in groupbyelem(writer_commission_lines, itemgetter(group))]
        else:
            grouped_commission_lines = writer_commission_lines

        values.update({
            "page_name": "Writer Commission Report",
            "pager": pager,
            "default_url": "/my/writer_commission_lines",
            "searchbar_groupby": searchbar_groupby,
            "searchbar_inputs": searchbar_inputs,
            "sortby": sortby,
            "filterby": filterby,
            "search": search,
            "search_in": search_in,
            "groupby": groupby,
            "grouped_commission_lines": grouped_commission_lines
        })

        return request.render("writer.portal_my_writer_commission_lines", values)

    def _writer_commission_line_get_page_view_values(self, commission_line, access_token, **kwargs):
        values = {
            "page_name": "Writer Commission Report",
            "writer_commission_line": commission_line
        }
        return self._get_page_view_values(commission_line, access_token, values, "my_writer_commission_lines_history",
                                          False, **kwargs)

    @http.route(["/my/writer_commission_lines/<int:commission_line_id>"], type="http", auth="user",
                website=True)
    def portal_my_writer_commission(self, commission_line_id, access_token=None, **kw):
        try:
            if not request.env.user.employee_id.is_writer:
                return request.redirect("/my")

            commission_line = self._document_check_access("writer.commission.line", commission_line_id, access_token)
        except (AccessError, MissingError):
            return request.redirect("/my")

        values = self._writer_commission_line_get_page_view_values(commission_line, access_token, **kw)
        return request.render("writer.portal_my_writer_commission_line", values)

    def _prepare_columns_writer_commission_lines_epxort(self):
        return [
            ("type", _("Type"), "selection"),
            ("product_template_id/display_name", _("Product"), "char"),
            ("product_category_id/display_name", _("Product Category"), "char"),
            ("date", _("Date"), "date"),
            ("amount", _("Amount"), "monetary"),
            ("state", _("Status"), "selection")
        ]

    def _prepare_export_writer_commissions_data(self, writer_commission_line_ids, groupby):
        groupby_mapping = self._get_writer_commissions_get_groupby_mapping()
        group = groupby_mapping.get(groupby)

        # export fields
        fields = []
        for column in self._prepare_columns_writer_commission_lines_epxort():
            fields.append({
                "name": column[0],
                "label": column[1],
                "type": column[2]
            })

        return {
            "import_compat": False,
            "model": "writer.commission.line",
            "ids": writer_commission_line_ids or request.session["my_writer_commission_lines_history"],
            "fields": fields,
            "domain": [],
            "groupby": group and [group] or [],
            "context": request.context
        }

    @http.route(["/my/writer_commission_lines/export"], type="http", auth="user", methods=["POST"], website=True,
                csrf=False)
    def portal_export_writer_commissions(self, **kw):
        export_writer_commission_line_ids = request.httprequest.form.get("export_writer_commission_line_ids", "")
        writer_commission_line_ids = []
        if export_writer_commission_line_ids:
            writer_commission_line_ids = export_writer_commission_line_ids.split(",")
            writer_commission_line_ids = [int(writer_commission_line_id) for writer_commission_line_id in
                                          writer_commission_line_ids]

        data = json.dumps(
            self._prepare_export_writer_commissions_data(writer_commission_line_ids, kw.get("groupby", False)))

        return request.redirect_query("/web/export/xlsx?%s" % keep_query('*', data=data))

    def _get_writer_target_lines_searchbar_groupby(self):
        values = {
            "none": {"input": "none", "label": _("None"), "order": 1},
            "target": {"input": "target", "label": _("Target"), "order": 2},
            "type": {"input": "type", "label": _("Type"), "order": 3}
        }

        return dict(sorted(values.items(), key=lambda item: item[1]["order"]))

    def _get_writer_target_lines_get_groupby_mapping(self):
        return {
            "target": "writer_target_id",
            "type": "type"
        }

    def _get_writer_target_lines_searchbar_inputs(self):
        values = {
            "all": {"input": "all", "label": _("Search in All"), "order": 1},
            "target": {"input": "target", "label": _("Search in Target"), "order": 2},
            "date_from": {"input": "date_from", "label": _("Search in Date From"), "order": 3},
            "date_to": {"input": "date_to", "label": _("Search in Date To"), "order": 4}
        }

        return dict(sorted(values.items(), key=lambda item: item[1]["order"]))

    def _get_writer_target_lines_search_domain(self, search_in, search):
        search_domain = []

        if search_in in ("target", "all"):
            search_domain.append([("writer_target_id", "ilike", search)])
        if search_in in ("date_from", "all"):
            search_domain.append([("date_from", "ilike", search)])
        if search_in in ("date_to", "all"):
            search_domain.append([("date_to", "ilike", search)])

        return OR(search_domain)

    def _get_writer_target_lines_searchbar_filters(self):
        values = {
            "all": {"label": _("All"), "domain": []},
            "product_target": {"label": _("Product"), "domain": [("type", "=", "product")]},
            "product_category_target": {"label": _("Product Category"), "domain": [("type", "=", "product_category")]},
        }
        return OrderedDict(values)

    @http.route(["/my/writer_target_lines", "/my/writer_target_lines/page/<int:page>"], type="http", auth="user",
                website=True)
    def portal_my_writer_target_lines(self, page=1, sortby=None, filterby=None, search=None, search_in="all",
                                      groupby="none"):
        if not request.env.user.employee_id.is_writer:
            return request.redirect("/my")

        values = self._prepare_portal_layout_values()
        searchbar_groupby = self._get_writer_target_lines_searchbar_groupby()
        searchbar_inputs = self._get_writer_target_lines_searchbar_inputs()
        searchbar_filters = self._get_writer_target_lines_searchbar_filters()

        domain = [("writer_id", "=", request.env.user.employee_id.id)]

        # filter
        if not filterby:
            filterby = "all"

        domain += searchbar_filters[filterby]["domain"]

        # search
        if search and search_in:
            domain += self._get_writer_target_lines_search_domain(search_in, search)

        writer_target_line_obj = request.env["writer.target.line"]

        # writer target lines count
        writer_target_lines_count = writer_target_line_obj.search_count(domain)

        # pager
        pager = portal_pager(
            url="/my/writer_target_lines",
            url_args={"sortby": sortby, "groupby": groupby, "search_in": search_in, "search": search,
                      "filterby": filterby},
            total=writer_target_lines_count,
            page=page,
            step=self._items_per_page)

        writer_target_lines = writer_target_line_obj.search(domain, limit=self._items_per_page,
                                                            offset=pager["offset"])

        request.session["my_writer_target_lines_history"] = writer_target_lines.ids[:100]

        groupby_mapping = self._get_writer_target_lines_get_groupby_mapping()
        group = groupby_mapping.get(groupby)

        if group:
            grouped_writer_target_lines = [writer_target_line_obj.concat(*g) for k, g in
                                           groupbyelem(writer_target_lines, itemgetter(group))]
        else:
            grouped_writer_target_lines = writer_target_lines

        values.update({
            "page_name": "Writer Target Report",
            "pager": pager,
            "default_url": "/my/writer_target_lines",
            "searchbar_groupby": searchbar_groupby,
            "searchbar_inputs": searchbar_inputs,
            "searchbar_filters": searchbar_filters,
            "sortby": sortby,
            "filterby": filterby,
            "search": search,
            "search_in": search_in,
            "groupby": groupby,
            "grouped_target_lines": grouped_writer_target_lines
        })

        return request.render("writer.portal_my_writer_target_lines", values)

    def _prepare_columns_writer_target_lines_epxort(self):
        return [
            ("writer_target_id/display_name", _("Target Name"), "char"),
            ("date_from", _("Date From"), "date"),
            ("date_to", _("Date To"), "date"),
            ("type", _("Type"), "selection"),
            ("target", _("Target"), "integer"),
            ("target_achieved", _("Target Achieved"), "integer")
        ]

    def _prepare_export_writer_target_lines_data(self, writer_target_line_ids, groupby):
        groupby_mapping = self._get_writer_target_lines_get_groupby_mapping()
        group = groupby_mapping.get(groupby)

        # export fields
        fields = []
        for column in self._prepare_columns_writer_target_lines_epxort():
            fields.append({
                "name": column[0],
                "label": column[1],
                "type": column[2]
            })

        return {
            "import_compat": False,
            "model": "writer.target.line",
            "ids": writer_target_line_ids or request.session["my_writer_target_lines_history"],
            "fields": fields,
            "domain": [],
            "groupby": group and [group] or [],
            "context": request.context
        }

    @http.route(["/my/writer_target_lines/export"], type="http", auth="user", methods=["POST"], website=True,
                csrf=False)
    def portal_export_writer_target_lines(self, **kw):
        export_writer_target_line_ids = request.httprequest.form.get("export_writer_target_line_ids", "")
        writer_target_line_ids = []
        if export_writer_target_line_ids:
            writer_target_line_ids = export_writer_target_line_ids.split(",")
            writer_target_line_ids = [int(writer_target_line_id) for writer_target_line_id in writer_target_line_ids]

        data = json.dumps(
            self._prepare_export_writer_target_lines_data(writer_target_line_ids, kw.get("groupby", False)))

        return request.redirect_query("/web/export/xlsx?%s" % keep_query('*', data=data))

    def _get_writer_product_brands_searchbar_inputs(self):
        values = {
            "all": {"input": "all", "label": _("Search in All"), "order": 1},
            "name": {"input": "name", "label": _("Search in Name"), "order": 2}
        }

        return dict(sorted(values.items(), key=lambda item: item[1]["order"]))

    def _get_writer_product_brands_search_domain(self, search_in, search):
        search_domain = []

        if search_in in ("name", "all"):
            search_domain.append([("name", "ilike", search)])

        return OR(search_domain)

    @http.route(["/my/writer_product_brands", "/my/writer_product_brands/page/<int:page>"], type="http",
                auth="user", website=True)
    def portal_my_writer_product_brands(self, page=1, sortby=None, filterby=None, search=None, search_in="all",
                                        groupby="none"):
        if not request.env.user.employee_id.is_writer:
            return request.redirect("/my")

        values = self._prepare_portal_layout_values()
        searchbar_inputs = self._get_writer_product_brands_searchbar_inputs()
        domain = [("id", "in",
                   request.env["product.template"].search([("writer_id", "=", request.env.user.employee_id.id)]).mapped(
                       "brand_id").ids)]

        # search
        if search and search_in:
            domain += self._get_writer_product_brnads_search_domain(search_in, search)

        product_brand_obj = request.env["product.brand"]

        # writer product brands count
        writer_product_brands_count = product_brand_obj.search_count(domain)

        # pager
        pager = portal_pager(
            url="/my/writer_product_brands",
            url_args={"sortby": sortby, "groupby": groupby, "search_in": search_in, "search": search,
                      "filterby": filterby},
            total=writer_product_brands_count,
            page=page,
            step=self._items_per_page)

        writer_product_brands = product_brand_obj.search(domain, limit=self._items_per_page, offset=pager["offset"])

        request.session["my_writer_product_brands_history"] = writer_product_brands.ids[:100]

        values.update({
            "page_name": "Writer Product Brand",
            "pager": pager,
            "default_url": "/my/writer_product_brands",
            "searchbar_inputs": searchbar_inputs,
            "sortby": sortby,
            "filterby": filterby,
            "search": search,
            "search_in": search_in,
            "groupby": groupby,
            "product_brands": writer_product_brands
        })

        return request.render("writer.portal_my_writer_product_brands", values)

    @http.route(["/my/writer_product_brands/edit/<int:id>"], type="http", auth="user", methods=["GET", "POST"],
                website=True, csrf=False)
    def portal_edit_writer_product_brand(self, id, access_token=None, **kw):
        if not request.env.user.employee_id.is_writer:
            return request.redirect("/my")

        product_brand = request.env["product.brand"].search([("id", "=", id), (
            "id", "in",
            request.env["product.template"].search([("writer_id", "=", request.env.user.employee_id.id)]).mapped(
                "brand_id").ids)], limit=1)
        if not product_brand:
            return request.redirect("/my/writer_product_brands")

        lang_code_en = request.env.ref("base.lang_en").code
        lang_ar = request.env.ref("base.lang_ar")
        lang_code_ar = False
        if lang_ar.active:
            lang_code_ar = lang_ar.code

        if request.httprequest.method == "GET":
            return request.render("writer.portal_my_writer_product_brand_edit", {
                "page_name": "Writer Product Brand",
                "product_brand": product_brand,
                "lang_code_en": lang_code_en,
                "lang_code_ar": lang_code_ar
            })

        data = request.httprequest.form

        vals = {
            "name": data["name"],
            "description": data["description"],
            "seo_title": data["seo_title"],
            "seo_description": data["seo_description"]
        }

        edit_delete_image = data["edit_delete_image"]
        if edit_delete_image == "1":
            image = request.httprequest.files.getlist("image")
            vals.update({"image_1920": base64.b64encode(image[0].read())})
        elif edit_delete_image == "2":
            vals.update({"image_1920": False})

        product_brand.with_context(lang=lang_code_en).write(vals)


        if lang_code_ar:
            product_brand.with_context(lang=lang_code_ar).write({
                "name": data["name_arabic"],
                "description": data["description"],
                "seo_title": data["seo_title_arabic"],
                "seo_description": data["seo_description_arabic"]
            })

            # update arabic description
            self.action_portal_writer_update_html_field(product_brand, "description", data["description_arabic"],
                                                        lang_code_ar, lang_code_en)

        return request.redirect("/my/writer_product_brands")


    def _get_writer_product_tags_searchbar_inputs(self):
        values = {
            "all": {"input": "all", "label": _("Search in All"), "order": 1},
            "name": {"input": "name", "label": _("Search in Name"), "order": 2}
        }

        return dict(sorted(values.items(), key=lambda item: item[1]["order"]))

    def _get_writer_product_tags_search_domain(self, search_in, search):
        search_domain = []

        if search_in in ("name", "all"):
            search_domain.append([("name", "ilike", search)])

        return OR(search_domain)

    @http.route(["/my/writer_product_tags", "/my/writer_product_tags/page/<int:page>"], type="http",
                auth="user", website=True)
    def portal_my_writer_product_tags(self, page=1, sortby=None, filterby=None, search=None, search_in="all",
                                      groupby="none"):
        if not request.env.user.employee_id.is_writer:
            return request.redirect("/my")

        values = self._prepare_portal_layout_values()
        searchbar_inputs = self._get_writer_product_tags_searchbar_inputs()
        domain = [("id", "in",
                   request.env["product.template"].search([("writer_id", "=", request.env.user.employee_id.id)]).mapped(
                       "product_tag_ids").ids)]

        # search
        if search and search_in:
            domain += self._get_writer_product_tags_search_domain(search_in, search)

        product_tag_obj = request.env["product.tag"]

        # writer product tags count
        writer_product_tags_count = product_tag_obj.search_count(domain)

        # pager
        pager = portal_pager(
            url="/my/writer_product_tags",
            url_args={"sortby": sortby, "groupby": groupby, "search_in": search_in, "search": search,
                      "filterby": filterby},
            total=writer_product_tags_count,
            page=page,
            step=self._items_per_page)

        writer_product_tags = product_tag_obj.search(domain, limit=self._items_per_page, offset=pager["offset"])

        request.session["my_writer_product_tags_history"] = writer_product_tags.ids[:100]

        values.update({
            "page_name": "Writer Product Tag",
            "pager": pager,
            "default_url": "/my/writer_product_tags",
            "searchbar_inputs": searchbar_inputs,
            "sortby": sortby,
            "filterby": filterby,
            "search": search,
            "search_in": search_in,
            "groupby": groupby,
            "product_tags": writer_product_tags
        })

        return request.render("writer.portal_my_writer_product_tags", values)

    @http.route(["/my/writer_product_tags/edit/<int:id>"], type="http", auth="user", methods=["GET", "POST"],
                website=True, csrf=False)
    def portal_edit_writer_product_tag(self, id, access_token=None, **kw):
        if not request.env.user.employee_id.is_writer:
            return request.redirect("/my")

        product_tag = request.env["product.tag"].search([("id", "=", id), (
            "id", "in",
            request.env["product.template"].search([("writer_id", "=", request.env.user.employee_id.id)]).mapped(
                "product_tag_ids").ids)], limit=1)
        if not product_tag:
            return request.redirect("/my/writer_product_tags")

        lang_code_en = request.env.ref("base.lang_en").code
        lang_ar = request.env.ref("base.lang_ar")
        lang_code_ar = False
        if lang_ar.active:
            lang_code_ar = lang_ar.code

        if request.httprequest.method == "GET":
            return request.render("writer.portal_my_writer_product_tag_edit", {
                "page_name": "Writer Product Tag",
                "product_tag": product_tag,
                "lang_code_en": lang_code_en,
                "lang_code_ar": lang_code_ar
            })

        data = request.httprequest.form
        product_tag.with_context(lang=lang_code_en).write({
            "name": data["name"],
            "description": data["description"],
            "seo_title": data["seo_title"],
            "seo_description": data["seo_description"]
        })

        if lang_code_ar:
            product_tag.with_context(lang=lang_code_ar).write({
                "name": data["name_arabic"],
                "description": data["description"],
                "seo_title": data["seo_title_arabic"],
                "seo_description": data["seo_description_arabic"]
            })

            # update arabic description
            self.action_portal_writer_update_html_field(product_tag, "description", data["description_arabic"],
                                                        lang_code_ar, lang_code_en)

        # add or edit or delete faqs
        add_faqs = {}
        edit_faqs = {}
        delete_faqs = data["delete_faqs"]
        delete_faqs = delete_faqs and eval(delete_faqs) or []
        delete_faqs = [int(delete_faq) for delete_faq in delete_faqs]

        for key, val in data.items():
            if "add_faq" in key or "edit_faq" in key:
                key_list = key.split("_")
                field_key = "_".join(key_list[2:len(key_list) - 1])
                faq_id = key_list[-1]

                if key_list[0] == "add":
                    if faq_id not in add_faqs:
                        add_faqs.update({key_list[-1]: {}})

                    add_faqs[faq_id].update({field_key: val})
                else:
                    if faq_id not in edit_faqs:
                        edit_faqs.update({key_list[-1]: {}})

                    edit_faqs[faq_id].update({field_key: val})

        if delete_faqs:
            faqs = product_tag.faq_ids.filtered(lambda f: f.id in delete_faqs)
            if faqs:
                faqs.unlink()

        product_tag_faq_obj = request.env["product.tag.faq"]
        for faq_id, faq_vals in edit_faqs.items():
            faq = product_tag_faq_obj.browse(int(faq_id))
            if faq.exists():
                faq.write({
                    "quotation": faq_vals["quotation"],
                    "answer": faq_vals["answer"],
                })

                if lang_code_ar:
                    faq.with_context(lang=lang_code_ar).write({
                        "quotation": faq_vals["quotation_arabic"],
                        "answer": faq_vals["answer_arabic"],
                    })

        for faq_id, faq_vals in add_faqs.items():
            faq = product_tag_faq_obj.create({
                "quotation": faq_vals["quotation"],
                "answer": faq_vals["answer"],
                "product_tag_id": product_tag.id
            })

            if lang_code_ar:
                faq.with_context(lang=lang_code_ar).write({
                    "quotation": faq_vals["quotation_arabic"],
                    "answer": faq_vals["answer_arabic"],
                })

        return request.redirect("/my/writer_product_tags")
