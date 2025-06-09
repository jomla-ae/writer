# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.exceptions import ValidationError


class WriterTarget(models.Model):
    _name = "writer.target"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Writer Target"

    name = fields.Char(string="Name", required=True, tracking=True, indext=True, translate=True)
    writer_id = fields.Many2one("hr.employee", string="Writer", required=True, tracking=True,
                                domain="[('is_writer','=',True),('company_id','=',company_id)]")
    date_from = fields.Date(string="Date From", required=True, tracking=True,
                            default=lambda self: fields.Date.today() + relativedelta(day=1), copy=False)
    date_to = fields.Date(string="Date To", required=True, tracking=True,
                          default=lambda self: fields.Date.today() + relativedelta(day=31), copy=False)
    company_id = fields.Many2one("res.company", string="Company", tracking=True, default=lambda self: self.env.company)
    line_ids = fields.One2many("writer.target.line", "writer_target_id", string="Lines", copy=True)

    @api.constrains("date_from", "date_to", "writer_id", "company_id")
    def _check_date(self):
        for writer_target in self:
            if writer_target.date_from > writer_target.date_to:
                raise ValidationError(_("Date from must be less than or equal to date to"))

            if self.search_count([("id", "!=", writer_target.id), ("writer_id", "=", writer_target.writer_id.id),
                                  ("date_from", "<=", writer_target.date_from),
                                  ("date_to", ">=", writer_target.date_from), "|", ("company_id", "=", False),
                                  ("company_id", "=", writer_target.company_id.id)]):
                raise ValidationError(
                    _("Can't select writer %s for same period" % writer_target.writer_id.display_name))


class WriterTargetLine(models.Model):
    _name = "writer.target.line"
    _description = "Writer Target Line"

    writer_target_id = fields.Many2one("writer.target", string="Writer Target", ondelete="cascade", required=True)
    writer_id = fields.Many2one(related="writer_target_id.writer_id", string="Writer", store=True, readonly=True)
    date_from = fields.Date(related="writer_target_id.date_from", string="Date From", store=True, readonly=True)
    date_to = fields.Date(related="writer_target_id.date_to", string="Date To", store=True, readonly=True)
    type = fields.Selection([
        ("product", "Product"),
        ("product_category", "Product Category")], string="Type", required=True)
    target = fields.Integer(string="Target", required=True)
    target_achieved = fields.Integer(compute="_compute_target_achieved", string="Target Achieved", required=True)

    @api.constrains("type")
    def _check_target_type(self):
        for line in self:
            if self.search_count([("id", "!=", line.id), ("type", "=", line.type),
                                  ("writer_target_id", "=", line.writer_target_id.id)]) != 0:
                raise ValidationError(_("Can't duplicate target type for same target"))

    def _compute_target_achieved(self):
        writer_commission_line_obj = self.env["writer.commission.line"]

        for line in self:
            domain = [("writer_id", "=", line.writer_target_id.writer_id.id), ("state", "in", ["draft", "posted"]),
                      ("type", "=", line.type), ("date", ">=", line.writer_target_id.date_from),
                      ("date", "<=", line.writer_target_id.date_to)]
            if line.writer_target_id.company_id:
                domain += [("company_id", "=", line.writer_target_id.company_id.id)]

            line.target_achieved = writer_commission_line_obj.search_count(domain)

    def export_data(self, fields_to_export):
        if self.env.user.has_group("base.group_portal"):
            return super(WriterTargetLine, self.with_user(SUPERUSER_ID)).export_data(fields_to_export)

        return super().export_data(fields_to_export)
