# -*- coding: utf-8 -*-

from odoo import fields, models


class AssignWriterWizard(models.TransientModel):
    _name = "assign.writer"
    _description = "Assign Writer"

    writer_id = fields.Many2one("hr.employee", string="Writer", required=True, domain=[("is_writer", "=", True)])
    type = fields.Selection([
        ("product", "Product"),
        ("product_category", "Product Category")
    ], string="Type", required=True)

    def action_assign_writer(self):
        if self.type == "product":
            product_templates = self.env["product.template"].browse(self._context.get("active_ids", False))
            product_templates.write({"writer_id": self.writer_id.id})
        else:
            product_categories = self.env["product.category"].browse(self._context.get("active_ids", False))
            product_categories.write({"writer_id": self.writer_id.id})

        return True
