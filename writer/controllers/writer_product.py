from odoo import _
from odoo.osv.expression import OR


def get_searchbar_groupby():
    values = {
        "none": {
            "input": "none",
            "label": _("None"),
            "order": 1,
        },
        "category": {
            "input": "category",
            "label": _("Category"),
            "order": 2,
        },
        "brand": {
            "input": "brand",
            "label": _("Brand"),
            "order": 3,
        },
        "state": {
            "input": "state",
            "label": _("Status"),
            "order": 4,
        },
    }
    return dict(sorted(values.items(), key=lambda item: item[1]["order"]))


def get_groupby_mapping():
    return {
        "category": "categ_id",
        "brand": "brand_id",
        "state": "state",
    }


def get_searchbar_inputs():
    values = {
        "all": {
            "input": "all",
            "label": _("Search in All"),
            "order": 1,
        },
        "name": {
            "input": "name",
            "label": _("Search in Name"),
            "order": 2,
        },
        "internal_reference": {
            "input": "internal_reference",
            "label": _("Search in Internal Reference"),
            "order": 3,
        },
        "brand": {
            "input": "brand",
            "label": _("Search in Brand"),
            "order": 4,
        },
        "tags": {
            "input": "tags",
            "label": _("Search in Product Tags"),
            "order": 5,
        },
    }

    return dict(sorted(values.items(), key=lambda item: item[1]["order"]))


def get_search_domain(search_in, search):
    domain = [("state", "!=", "published")]

    search_domain = []
    if search_in and search:
        if search_in in ("name", "all"):
            search_domain.append([("name", "ilike", search)])

        if search_in in ("internal_reference", "all"):
            search_domain.append([("default_code", "ilike", search)])

        if search_in in ("brand", "all"):
            search_domain.append([("brand_id", "ilike", search)])

        if search_in in ("tags", "all"):
            search_domain.append([("product_tag_ids", "ilike", search)])
    if search_domain:
        return domain + OR(search_domain)
    else:
        return domain
