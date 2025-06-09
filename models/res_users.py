# -*- coding: utf-8 -*-

from odoo import models
from odoo.exceptions import ValidationError


class ResUsers(models.AbstractModel):
    _inherit = "res.users"

    def get_writer_price_rule(self):
        pricelist = self.env["writer.pricelist"].search([("writer_ids", "in", self.id)], limit=1)

        if not pricelist:
            raise ValidationError(f"Writer {self.display_name} isn't in a pricelist")

        return pricelist and pricelist[0] or False

    # writer_commission_line_count = fields.Integer(compute="_compute_writer_commission_line_count")
    # def _compute_writer_commission_line_count(self):
    #     writer_commission_line = self.env["writer.commission.line"].sudo()
    #     for employee in self:
    #         employee.writer_commission_line_count = writer_commission_line.search_count([("writer_id", "=", employee.id)])
    # def action_get_writer_commission_lines(self):
    #     action = self.sudo().env.ref("writer.writer_commission_line_action")
    #     result = action.read()[0]
    #     result["domain"] = [("writer_id", "=", self.id)]
    #
    #     return result
