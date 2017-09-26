# -*- coding: utf-8 -*-

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
        selection=[("1", "Spouse"), ("3", "Offspring"), ("4", "Other family"),
                   ("9", "Not family")])

    # fecha de nacimiento
    birthday = fields.Date("Birthday")
