# -*- coding: utf-8 -*-

from odoo import models
from odoo.exceptions import ValidationError


class ResUsers(models.AbstractModel):
    _inherit = "res.users"

    def get_writer_price_rule(self):
        pricelist = self.env["writer.pricelist"].search([("writer_ids", "in", self.id)], limit=1)

        if not pricelist:
            raise ValidationError(f"Writer {self.display_name} isn't in a pricelist")

        return pricelist and pricelist[0] or False
