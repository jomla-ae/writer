# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api


class WriterTarget(models.Model):
    _name = "writer.target"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Writer Target"

    writer_id = fields.Many2one(
        "res.users",
        string="Writer",
        required=True,
        tracking=True,
        domain=lambda self: [("groups_id", "in", self.env.ref("writer.group_writer").id)],
    )
    date_from = fields.Date(
        string="Date From", required=True, tracking=True, default=lambda self: fields.Date.today(), copy=False
    )
    date_to = fields.Date(string="Date To", tracking=True, compute="_compute_date_to", copy=False, store=True)

    @api.depends("date_from")
    def _compute_date_to(self):
        for record in self:
            record.date_to = self._get_last_day_of_month(record.date_from)

    target = fields.Integer(string="Target", required=True)
    target_achieved = fields.Integer(compute="_compute_target_achieved", string="Target Achieved", required=True)

    def name_get(self):
        return [(record.id, record.writer_id.display_name) for record in self]

    """ @api.constrains("date_from", "date_to", "writer_id")
    def _check_date(self):
        for writer_target in self:
            if writer_target.date_from > writer_target.date_to:
                raise ValidationError(_("Date from must be less than or equal to date to"))

            if (
                self.search_count(
                    [
                        ("id", "!=", writer_target.id),
                        ("writer_id", "=", writer_target.writer_id.id),
                        ("date_from", "<=", writer_target.date_from),
                        ("date_to", ">=", writer_target.date_from),
                    ]
                )
                > 0
            ):
                raise ValidationError(_(f"Can't select writer {writer_target.writer_id.display_name} in overlapping periods")) """

    def _compute_target_achieved(self):
        writer_commission_line = self.env["writer.commission.line"]
        for record in self:
            record.target_achieved = writer_commission_line.search_count(
                domain=[
                    ("writer_id", "=", record.writer_id.id),
                    ("state", "in", ["draft", "posted"]),
                    ("date", ">=", record.date_from),
                    ("date", "<=", record.date_to),
                ]
            )

    @api.model
    def cron_create_targets(self, record_id):
        record = self.search([("id", "=", record_id)], limit=1)
        new_date_from = record.date_to + relativedelta(days=1)
        self.create(
            {
                "writer_id": record.writer_id.id,
                "target": record.target,
                "date_from": new_date_from,
                "date_to": self._get_last_day_of_month(new_date_from),
            }
        )

    @api.model
    def create(self, vals):
        record = super(WriterTarget, self).create(vals)
        # The Writer Manager doesn't need access to ir.cron any other time than this one.
        self.env["ir.cron"].sudo().create(
            {
                "name": f"Renew Writer Targets: {record.writer_id.name}",
                "model_id": self.env.ref("writer.model_writer_target").id,
                "state": "code",
                "code": f"model.cron_create_targets({record.id})",
                "numbercall": 1,
                "nextcall": record.date_to + relativedelta(days=1),
            }
        )
        return record

    @staticmethod
    def _get_last_day_of_month(today):
        next_month = today + relativedelta(days=35)
        return next_month - relativedelta(days=next_month.day)
