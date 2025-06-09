# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class WriterPriceList(models.Model):
    _name = "writer.pricelist"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Writer Pricelist"

    name = fields.Char(string="Name", required=True, tracking=True, indext=True, translate=True)
    writer_id = fields.Many2one("hr.employee", string="Writer", required=True, tracking=True,
                                domain="[('is_writer','=',True),('company_id','=',company_id)]")
    company_id = fields.Many2one("res.company", string="Company", tracking=True, required=True,
                                 default=lambda self: self.env.company)
    currency_id = fields.Many2one("res.currency", string="Currency", required=True, tracking=True,
                                  default=lambda self: self.env.company.currency_id)
    line_ids = fields.One2many("writer.pricelist.line", "writer_pricelist_id", string="Lines", copy=True)

    @api.constrains("writer_id", "company_id")
    def _check_writer_id(self):
        for writer_priclist in self:
            if self.search_count(
                    [("id", "!=", writer_priclist.id), ("company_id", "=", writer_priclist.company_id.id),
                     ("writer_id", "=", writer_priclist.writer_id.id)]) != 0:
                raise ValidationError(
                    _("Can't select writer %s because which have already pricelist" % writer_priclist.writer_id.display_name))

    @api.constrains("line_ids")
    def _check_lines(self):
        for writer_priclist in self:
            if not writer_priclist.line_ids.filtered(
                    lambda l: l.type == "by_category" and l.category_applied_on == "all"):
                raise ValidationError("Must be there price rule for all categories")

            if not writer_priclist.line_ids.filtered(
                    lambda l: l.type == "by_product" and l.product_applied_on == "all"):
                raise ValidationError("Must be there price rule for all products")


class WriterPriceListLine(models.Model):
    _name = "writer.pricelist.line"
    _description = "Writer Pricelist Line"

    writer_pricelist_id = fields.Many2one("writer.pricelist", string="Write PriceList", ondelete="cascade",
                                          required=True)
    name = fields.Char(string="Name", required=True, indext=True, translate=True)
    company_id = fields.Many2one(related="writer_pricelist_id.company_id", string="Currency", readonly=True, store=True)
    currency_id = fields.Many2one(related="writer_pricelist_id.currency_id", string="Currency", readonly=True,
                                  store=True)
    price = fields.Monetary(string="Price", required=True)
    type = fields.Selection([
        ("by_category", "By Category"),
        ("by_product", "By Product")], string="Type", required=True, default="by_category")

    category_applied_on = fields.Selection([("all", "All"), ("special", "Special")], string="Applied On", required=True,
                                           default="all")
    product_applied_on = fields.Selection([("all", "All"), ("category", "Category"), ("special", "Special")],
                                          string="Applied On", required=True, default="all")
    product_category_ids = fields.Many2many("product.category", string="Product Categories")
    product_template_ids = fields.Many2many("product.template", string="Products",
                                            domain="['|',('company_id','=',False),('company_id','=',company_id)]")

    @api.constrains("price")
    def _check_price(self):
        for line in self:
            if line.price <= 0:
                raise ValidationError(_("Price must be positive"))

    @api.onchange("type")
    def onchange_type(self):
        self.category_applied_on = "all"
        self.product_applied_on = "all"
