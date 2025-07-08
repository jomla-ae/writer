from odoo import fields, models


class AssignWriterWizard(models.TransientModel):
    _name = "assign.writer"
    _description = "Assign Writer"

    writer_id = fields.Many2one("res.users", string="Writer", required=True, domain=lambda self: [("groups_id", "in", self.env.ref("writer.group_writer").id)])

    def action_assign_writer(self):
        product_templates = self.env["product.template"].browse(self._context.get("active_ids", False))
        product_templates.write({"writer_id": self.writer_id.id})
        return True
