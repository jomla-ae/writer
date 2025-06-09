# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductCategory(models.Model):
    _inherit = "product.category"

    writer_id = fields.Many2one("hr.employee", string="Writer", tracking=True,
                                domain=[("is_writer", "=", True)])

    def _action_assign_writer(self):
        action = self.sudo().env.ref("writer.action_assign_writer_wizard")
        result = action.read()[0]

        result["context"] = {"default_type": "product_category"}

        return result

    def _prepare_writer_commission_line(self):
        price_rule = self.writer_id.get_writer_price_rule(type="by_category")

        return {
            "writer_id": self.writer_id.id,
            "product_category_id": self.id,
            "type": "product_category",
            "company_id": price_rule.company_id.id,
            "currency_id": price_rule.currency_id.id,
            "amount": price_rule.price
        }

    def action_publish(self):
        super().action_publish()

        writer_commission_line_obj = self.env["writer.commission.line"]
        for category in self.filtered(lambda c: c.writer_id and c.state == "published"):
            if writer_commission_line_obj.search_count(
                    [("writer_id", "=", category.writer_id.id), ("product_category_id", "=", category.id)]) == 0:
                writer_commission_line_obj.create(category._prepare_writer_commission_line())
