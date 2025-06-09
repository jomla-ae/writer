# -*- coding: utf-8 -*-

from itertools import groupby
from operator import itemgetter

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class WriterCommissionLine(models.Model):
    _name = "writer.commission.line"
    _inherit = ["mail.thread", "mail.activity.mixin", "portal.mixin"]
    _description = "Writer Commission Line"

    writer_id = fields.Many2one("res.users", string="Writer", domain=lambda self: [("groups_id", "in", self.env.ref("writer.group_writer").id)])
    date = fields.Date(string="Date", required=True, default=lambda self: fields.Date.context_today(self))
    product_template_id = fields.Many2one("product.template", string="Product")
    amount = fields.Monetary(string="Amount", tracking=True)
    state = fields.Selection([("draft", "Draft"), ("posted", "Posted"), ("cancel", "Cancelled")], string="Status", index=True, default="draft", required=True, tracking=True)
    currency_id = fields.Many2one("res.currency", string="Currency", required=True)
    invoice_id = fields.Many2one("account.move", string="Bill", copy=False)
    payment_state = fields.Selection(related="invoice_id.payment_state", string="Payment Status", store=True)

    def _compute_access_url(self):
        super()._compute_access_url()
        for writer_commission_line in self:
            writer_commission_line.access_url = f"/my/writer_commission_lines/{writer_commission_line.id}"

    def name_get(self):
        return [(record.id, record.product_template_id.name) for record in self]

    def action_confirm(self):
        writer_commission_lines = self.filtered(lambda l: l.state == "draft")
        if writer_commission_lines:
            config_parameter_obj = self.env["ir.config_parameter"].sudo()
            writer_commission_product = config_parameter_obj.get_param("writer.writer_commission_product_id", False)
            writer_commission_journal = config_parameter_obj.get_param("writer.writer_commission_journal_id", False)

            if not writer_commission_product or not writer_commission_journal:
                raise ValidationError(_("Please check settings writer commission in configuration"))

            writer_commission_product = int(writer_commission_product)
            writer_commission_journal = int(writer_commission_journal)

            account_move_obj = self.env["account.move"]
            writers = writer_commission_lines.mapped("writer_id")
            for writer in writers:
                commission_lines = writer_commission_lines.filtered(lambda l: l.writer_id == writer)
                if commission_lines:
                    if len(commission_lines.mapped("currency_id")) > 1:
                        raise ValidationError(_("Must be select commission lines same currency for writer %s" % writer.name))

                    date = max(commission_lines.mapped("date"))
                    reference = ",".join(commission_line.display_name for commission_line in commission_lines)
                    amount = sum(commission_line.amount for commission_line in commission_lines)

                    if amount == 0:
                        raise ValidationError(_("Cannot create bill because total amount equal to zero"))

                    currency_id = commission_lines[0].currency_id.id

                    invoice = account_move_obj.create(
                        {
                            "partner_id": writer.partner_id.id,
                            "journal_id": writer_commission_journal,
                            "invoice_date": date,
                            "invoice_origin": reference,
                            "company_id": commission_lines[0].writer_id.company_id.id,
                            "currency_id": currency_id,
                            "move_type": "in_invoice",
                            "invoice_line_ids": [
                                (
                                    0,
                                    0,
                                    {
                                        "product_id": writer_commission_product,
                                        "price_unit": abs(amount),
                                    },
                                )
                            ],
                        }
                    )
                    invoice.action_post()
                    commission_lines.write({"state": "posted", "invoice_id": invoice.id})

    def action_cancel(self):
        return self.filtered(lambda l: l.state != "cancel").write({"state": "cancel"})

    @api.model
    def cron_create_bills(self):
        writer_commission_lines = self.search([("state", "=", "draft")])
        for k, g in groupby(writer_commission_lines, key=itemgetter("currency_id")):
            lines = self.concat(*g)
            lines.action_confirm()

    def action_get_invoice(self):
        if not self.invoice_id:
            return None

        return {
            "name": self.invoice_id.name,
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "view_id": self.env.ref("account.view_move_form").id,
            "res_model": "account.move",
            "res_id": self.invoice_id.id,
        }
