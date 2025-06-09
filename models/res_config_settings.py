# -*- coding: utf-8 -*-

from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    writer_commission_product_id = fields.Many2one("product.product", config_parameter="writer.writer_commission_product_id")
    writer_commission_journal_id = fields.Many2one("account.journal", config_parameter="writer.writer_commission_journal_id")
