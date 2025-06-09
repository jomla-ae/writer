# -*- coding: utf-8 -*-

from odoo import models, fields, _
from odoo.exceptions import ValidationError


class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    is_writer = fields.Boolean(string="Is Writer", tracking=True)


class HrEmployee(models.AbstractModel):
    _inherit = "hr.employee"

    writer_commission_line_count = fields.Integer(compute="_compute_writer_commission_line_count",
                                                  string="Writer Commission Line Count")

    def _compute_writer_commission_line_count(self):
        writer_commission_line_obj = self.env["writer.commission.line"].sudo()
        for employee in self:
            employee.writer_commission_line_count = writer_commission_line_obj.search_count(
                [("writer_id", "=", employee.id)])

    def action_get_writer_commission_lines(self):
        action = self.sudo().env.ref("writer.action_writer_commission_lines")
        result = action.read()[0]

        result["domain"] = [("writer_id", "=", self.id)]

        return result

    def get_writer_price_rule(self, type=False, company_id=False):
        domain = [("writer_id", "=", self.id)]

        if company_id:
            domain += [("company_id", "=", company_id)]

        pricelist = self.env["writer.pricelist"].sudo().search(domain, limit=1)

        if not pricelist:
            raise ValidationError(_("Writer %s is not have pricelist" % self.display_name))

        if type == "by_category":
            pricelist_lines = pricelist.line_ids.filtered(
                lambda l: l.type == "by_category" and l.category_applied_on
                          == "special" and self.product_category_id in l.product_category_ids)
            if not pricelist_lines:
                pricelist_lines = pricelist.line_ids.filtered(
                    lambda l: l.type == "by_category" and l.category_applied_on == "all")
        else:
            pricelist_lines = pricelist.line_ids.filtered(
                lambda l: l.type == "by_product" and l.product_applied_on
                          == "special" and self.product_template_id in l.product_template_ids)
            if not pricelist_lines:
                pricelist_lines = pricelist.line_ids.filtered(
                    lambda l: l.type == "by_product" and l.product_applied_on
                              == "category" and self.product_template_id.categ_id in l.product_category_ids)

                if not pricelist_lines:
                    pricelist_lines = pricelist.line_ids.filtered(
                        lambda l: l.type == "by_product" and l.product_applied_on == "all")

        if not pricelist_lines:
            raise ValidationError(_("Writer %s is not have price rule to get price" % self.display_name))

        return pricelist_lines and pricelist_lines[0] or False
