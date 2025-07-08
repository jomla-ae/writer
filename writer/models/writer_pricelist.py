# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class WriterPricelist(models.Model):
    _name = "writer.pricelist"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Writer Pricelist"

    writer_ids = fields.Many2many(
        "res.users",
        string="Writers",
        required=True,
        tracking=True,
        domain=lambda self: [("groups_id", "in", self.env.ref("writer.group_writer").id)],
    )

    price = fields.Monetary(string="Price", required=True)
    currency_id = fields.Many2one("res.currency", string="Currency", required=True, tracking=True, default=lambda self: self.env.company.currency_id)

    @api.constrains("price")
    def _check_price(self):
        for line in self:
            if line.price <= 0:
                raise ValidationError(_("Price must be positive"))

    @api.constrains("writer_ids")
    def _check_writer_id(self):
        for writer_priclist in self:
            for writer in writer_priclist.writer_ids:
                if self.search_count([("id", "!=", writer_priclist.id), ("writer_ids", "in", writer.id)]) != 0:
                    raise ValidationError(f"Can't select writer {writer.display_name} because which have already pricelist")

    def name_get(self):
        return [(rec.id, f"{rec.price} {rec.currency_id.symbol}: {', '.join([w.name for w in rec.writer_ids[:5]])}") for rec in self]
