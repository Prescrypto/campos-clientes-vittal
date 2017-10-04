# -*- coding: utf-8 -*-

import odoo
from datetime import date, datetime
from odoo import models, fields, api


class partner_member(models.Model):
    _name = "partner.member"
    _inherit = "res.partner"

    # padre del miembro
    parent_id = fields.Many2one(
        "res.partner", string="Parent", ondelete="set null")

    # titular del grupo
    is_owner = fields.Boolean("Owner")

    # condición de grupo
    relationship = fields.Selection(
        string="Relationship",
        selection=[("1", odoo._("Father")), ("2", odoo._("Mother")),
                   ("3", odoo._("Spouse")), ("4", odoo._("Offspring")),
                   ("5", odoo._("Other family"))])

    # fecha de nacimiento
    birthday = fields.Date("Birthday")

    # edad
    age = fields.Integer("Age", compute="_calc_age", store=False)

    @api.one
    @api.depends("birthday")
    def _calc_age(self):
        def calculate_age(born):
            today = date.today()
            return today.year - born.year - ((today.month, today.day) <
                                             (born.month, born.day))

        if self.birthday:
            self.age = calculate_age(
                fields.Datetime.from_string(self.birthday))

    # enfermedades previas
    prev_ailments = fields.Text("Previous Ailments")

    # alergias
    allergies = fields.Text("Allergies")

    # estatus
    user_active = fields.Boolean("Active")

    # comenzar suscripción
    @api.one
    def start_reg(self):
        self.start_date = fields.Datetime.to_string(datetime.now())
        self.end_date = ""
        self.user_active = True

    # terminar suscripción
    @api.one
    def end_reg(self):
        self.end_date = fields.Datetime.to_string(datetime.now())
        self.user_active = False

    # fecha de registro
    start_date = fields.Date("Registration Date")

    # fecha de baja
    end_date = fields.Date("Date Ended")

    # motivo de baja
    end_reason = fields.Text("Reason for Ending")

    # clave de socio
    associate_id = fields.Char("Associate ID")
