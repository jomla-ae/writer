# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    writer_id = fields.Many2one("hr.employee", string="Writer", tracking=True,
                                domain=[("is_writer", "=", True)])

    def _action_assign_writer(self):
        action = self.sudo().env.ref("writer.action_assign_writer_wizard")
        result = action.read()[0]

        result["context"] = {"default_type": "product"}

        return result

    def _prepare_writer_commission_line(self):
        price_rule = self.writer_id.get_writer_price_rule(company_id=self.company_id.id)

        return {
            "writer_id": self.writer_id.id,
            "product_template_id": self.id,
            "type": "product",
            "company_id": price_rule.company_id.id,
            "currency_id": price_rule.currency_id.id,
            "amount": price_rule.price
        }

    def action_publish(self):
        super().action_publish()

        writer_commission_line_obj = self.env["writer.commission.line"]
        for product_template in self.filtered(lambda p: p.writer_id and p.state == "published"):
            if writer_commission_line_obj.search_count(
                    [("writer_id", "=", product_template.writer_id.id),
                     ("product_template_id", "=", product_template.id)]) == 0:
                writer_commission_line_obj.create(product_template._prepare_writer_commission_line())
