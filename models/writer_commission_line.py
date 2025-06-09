# -*- coding: utf-8 -*-

from itertools import groupby
from operator import itemgetter

from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.exceptions import ValidationError


class WriterCommissionLine(models.Model):
    _name = "writer.commission.line"
    _inherit = ["mail.thread", "mail.activity.mixin", "portal.mixin"]
    _description = "Writer Commission Line"

    writer_id = fields.Many2one("hr.employee", string="Writer", readonly=True)
    date = fields.Date(string="Date", required=True, default=lambda self: fields.Date.context_today(self),
                       readonly=True)
    type = fields.Selection([
        ("product", "Product"),
        ("product_category", "Product Category")
    ], string="Type", required=True, index=True, readonly=True)
    product_template_id = fields.Many2one("product.template", string="Product", readonly=True)
    product_category_id = fields.Many2one("product.category", string="Product Category", readonly=True)
    amount = fields.Monetary(string="Amount", readonly=True, tracking=True)
    state = fields.Selection([
        ("draft", "Draft"),
        ("posted", "Posted"),
        ("cancel", "Cancelled")], string="Status", index=True, default="draft", required=True, readonly=True,
        tracking=True)
    currency_id = fields.Many2one("res.currency", string="Currency", readonly=True, required=True)
    company_id = fields.Many2one("res.company", string="Company", readonly=True, required=True)
    invoice_id = fields.Many2one("account.move", string="Bill", readonly=True, copy=False)
    payment_state = fields.Selection(related="invoice_id.payment_state", string="Payment Status", readonly=True,
                                     store=True)


    def _compute_access_url(self):
        super()._compute_access_url()
        for writer_commission_line in self:
            writer_commission_line.access_url = f"/my/writer_commission_lines/{writer_commission_line.id}"

    def name_get(self):
        res = []
        for writer_commission_line in self:
            if writer_commission_line.product_category_id:
                name = writer_commission_line.product_category_id.name

            else:
                name = writer_commission_line.product_template_id.name

            res += [(writer_commission_line.id, name)]

        return res

    def export_data(self, fields_to_export):
        if self.env.user.has_group("base.group_portal"):
            return super(WriterCommissionLine, self.with_user(SUPERUSER_ID)).export_data(fields_to_export)

        return super().export_data(fields_to_export)


    def _prepare_vendor_bill_line(self, product_id, amount):
        return {
            "product_id": product_id,
            "price_unit": abs(amount)
        }

    def _prepare_vendor_bill(self, writer, journal_id, date, invoice_lines, reference, company, currency):
        return {
            "partner_id": writer.user_id.partner_id.id,
            "journal_id": journal_id,
            "invoice_date": date,
            "invoice_origin": reference,
            "company_id": company.id,
            "currency_id": currency.id,
            "move_type": "in_invoice",
            "invoice_line_ids": invoice_lines
        }

    def action_confirm(self):
        writer_commission_lines = self.filtered(lambda l: l.state == "draft")
        if writer_commission_lines:
            config_parameter_obj = self.env["ir.config_parameter"].sudo()
            writer_commission_product = config_parameter_obj.sudo().get_param("writer.writer_commission_product_id",
                                                                              False)
            writer_commission_journal = config_parameter_obj.sudo().get_param("writer.writer_commission_journal_id",
                                                                              False)

            if not writer_commission_product or not writer_commission_journal:
                raise ValidationError(_("Please check settings writer commission in configuration"))

            writer_commission_product = int(writer_commission_product)
            writer_commission_journal = int(writer_commission_journal)

            account_move_obj = self.env["account.move"]
            writers = writer_commission_lines.mapped("writer_id")
            for writer in writers:
                commission_lines = writer_commission_lines.filtered(lambda l: l.writer_id == writer)
                if commission_lines:
                    if len(commission_lines.mapped("company_id")) > 1:
                        raise ValidationError(
                            _("Must be select commission lines same company for writer %s" % writer.name))

                    if len(commission_lines.mapped("currency_id")) > 1:
                        raise ValidationError(
                            _("Must be select commission lines same currency for writer %s" % writer.name))

                    lines = []
                    company = commission_lines[0].company_id
                    currency = commission_lines[0].currency_id
                    date = max(commission_lines.mapped("date"))
                    reference = ",".join(commission_line.display_name for commission_line in commission_lines)
                    amount = sum(commission_line.amount for commission_line in commission_lines)

                    if amount == 0:
                        raise ValidationError(_("Cannot create bill because total amount equal to zero"))

                    lines.append(
                        (0, 0, self._prepare_vendor_bill_line(writer_commission_product, amount)))

                    invoice = account_move_obj.create(
                        self._prepare_vendor_bill(writer, writer_commission_journal, date, lines,
                                                  reference, company, currency))
                    invoice.action_post()
                    commission_lines.write({"state": "posted", "invoice_id": invoice.id})

    def action_cancel(self):
        return self.filtered(lambda l: l.state != "cancel").write({"state": "cancel"})

    @api.model
    def cron_create_bills(self):
        writer_commission_lines = self.search([("state", "=", "draft")])
        for k, g in groupby(writer_commission_lines, key=itemgetter("company_id", "currency_id")):
            lines = self.concat(*g)
            lines.action_confirm()

    def action_get_invoice(self):
        if not self.invoice_id:
            return

        return {
            "name": self.invoice_id.name,
            "type": "ir.actions.act_window",
            "view_mode": "form",
            'view_id': self.env.ref("account.view_move_form").id,
            "res_model": "account.move",
            "res_id": self.invoice_id.id,
        }
