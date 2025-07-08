from odoo import _
from odoo.osv.expression import OR


def get_searchbar_inputs():
    values = {
        "all": {
            "input": "all",
            "label": _("Search in All"),
            "order": 1,
        },
        "target": {
            "input": "target",
            "label": _("Search in Target"),
            "order": 2,
        },
        "date_from": {
            "input": "date_from",
            "label": _("Search in Date From"),
            "order": 3,
        },
        "date_to": {
            "input": "date_to",
            "label": _("Search in Date To"),
            "order": 4,
        },
    }

    return dict(sorted(values.items(), key=lambda item: item[1]["order"]))


def get_search_domain(search_in, search):
    if not search_in or not search:
        return []

    search_domain = []

    if search_in in ("target", "all"):
        search_domain.append([("writer_target_id", "ilike", search)])
    if search_in in ("date_from", "all"):
        search_domain.append([("date_from", "ilike", search)])
    if search_in in ("date_to", "all"):
        search_domain.append([("date_to", "ilike", search)])

    if not search_domain:
        return []

    return OR(search_domain)


def prepare_columns_epxort():
    return [
        {
            "name": "date_from",
            "label": _("Date From"),
            "type": "date",
        },
        {
            "name": "date_to",
            "label": _("Date To"),
            "type": "date",
        },
        {
            "name": "target",
            "label": _("Target"),
            "type": "integer",
        },
        {
            "name": "target_achieved",
            "label": _("Target Achieved"),
            "type": "integer",
        },
    ]
