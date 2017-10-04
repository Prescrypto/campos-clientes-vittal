# -*- coding: utf-8 -*-

import odoo
from odoo import models, fields


class partner_member(models.Model):
    _name = "partner.member"
    _inherit = "res.partner"

    # número de socio
    member_id = fields.Char("Associate ID")

    # padre del miembro
    parent_id = fields.Many2one(
        "res.partner", string="Parent", ondelete="set null")

    # titular del grupo
    is_owner = fields.Boolean("Owner")

    # condición de grupo
    relationship = fields.Selection(
        string="Relationship",
        selection=[("1", odoo._("Spouse")), ("3", odoo._("Offspring")),
                   ("4", odoo._("Other family")), ("9", odoo._("Not family"))])

    # fecha de nacimiento
    birthday = fields.Date("Birthday")
