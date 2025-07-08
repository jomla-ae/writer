# -*- coding: utf-8 -*-

from odoo import models, api
from odoo.exceptions import ValidationError


class ResUsers(models.AbstractModel):
    _inherit = "res.users"

    def get_writer_price_rule(self):
        pricelist = self.env["writer.pricelist"].search([("writer_ids", "in", self.id)], limit=1)

        if not pricelist:
            raise ValidationError(f"Writer {self.display_name} isn't in a pricelist")

        return pricelist and pricelist[0] or False

    @api.model_create_multi
    def create(self, vals):
        user = super(ResUsers, self).create(vals)
        if user.login and user.partner_id and self.env.ref("writer.group_writer").id in user.groups_id.ids:
            user.partner_id.email = user.login

        return user