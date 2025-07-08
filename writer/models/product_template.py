# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    writer_id = fields.Many2one("res.users", string="Writer", tracking=True, domain=lambda self: [("groups_id", "in", self.env.ref("writer.group_writer").id)])
    writer_submit_date = fields.Date(string="Writer Submit Date", readonly=True)

    seo_title = fields.Char(string="SEO Title", tracking=True, translate=True)
    seo_description = fields.Text(string="SEO Description", tracking=True, translate=True)
    description_arabic = fields.Html("Description (Arabic)")

    def action_submit(self):
        super().action_submit()

        today = fields.Date.context_today(self)
        for record in self.filtered(lambda rec: rec.writer_id):
            record.writer_submit_date = today

    def action_publish(self):
        super().action_publish()

        writer_commission_line = self.env["writer.commission.line"]
        for product_template in self.filtered(lambda p: p.writer_id and p.state == "published"):
            if writer_commission_line.search_count([("writer_id", "=", product_template.writer_id.id), ("product_template_id", "=", product_template.id)]) == 0:
                price_rule = product_template.writer_id.get_writer_price_rule()
                writer_commission_line.create(
                    {
                        "writer_id": product_template.writer_id.id,
                        "product_template_id": product_template.id,
                        "currency_id": price_rule.currency_id.id,
                        "amount": price_rule.price,
                        "date": product_template.writer_submit_date,
                    }
                )

    def action_assign_writer(self):
        action = self.env.ref("writer.assign_writer_action")
        result = action.read()[0]
        return result
