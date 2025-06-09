from odoo import _
from odoo.osv.expression import OR


def prepare_columns_epxort():
    return [
        {
            "name": "product_template_id/display_name",
            "label": _("Product"),
            "type": "char",
        },
        {
            "name": "date",
            "label": _("Date"),
            "type": "date",
        },
        {
            "name": "amount",
            "label": _("Amount"),
            "type": "monetary",
        },
        {
            "name": "state",
            "label": _("Status"),
            "type": "selection",
        },
    ]


def get_searchbar_groupby():
    values = {
        "none": {
            "input": "none",
            "label": _("None"),
            "order": 1,
        },
        "date": {
            "input": "date",
            "label": _("Date"),
            "order": 2,
        },
        "product": {
            "input": "product",
            "label": _("Product"),
            "order": 4,
        },
        "state": {
            "input": "state",
            "label": _("Status"),
            "order": 6,
        },
    }

    return dict(sorted(values.items(), key=lambda item: item[1]["order"]))


def get_groupby_mapping():
    return {
        "state": "state",
        "date": "date",
        "product": "product_template_id",
    }


def get_searchbar_inputs():
    values = {
        "all": {
            "input": "all",
            "label": _("Search in All"),
            "order": 1,
        },
        "date": {
            "input": "date",
            "label": _("Search in Date"),
            "order": 2,
        },
    }
    return dict(sorted(values.items(), key=lambda item: item[1]["order"]))


def get_search_domain(search_in, search):
    if not search_in or not search:
        return []

    search_domain = []

    if search_in in ("date", "all"):
        search_domain.append([("date", "ilike", search)])

    if not search_domain:
        return []

    return OR(search_domain)


#
# def get_page_view_values(commission_line):
#     return {
#         "page_name": "Writer Commission Report",
#         "writer_commission_line": commission_line,
#     }
