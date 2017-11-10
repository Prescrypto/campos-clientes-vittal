# -*- coding: utf-8 -*-

import odoo
import logging
from datetime import date, datetime
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class UserMember(models.Model):
    _name = "user.member"
    _inherit = "res.partner"

    # padre del miembro
    parent_id = fields.Many2one("res.partner", string="Parent")

    # clave de socio
    associate_id = fields.Char("Associate ID")

    # condición de grupo
    relationship = fields.Selection(string="Relationship", selection=[])

    # titular del grupo
    is_owner = fields.Boolean("Owner")

    # fecha de nacimiento
    birthday = fields.Date("Birthday")

    # edad
    age = fields.Integer("Age", compute="_calc_age", store=False)

    @api.multi
    @api.depends("birthday")
    def _calc_age(self):
        for record in self:
            def calculate_age(born):
                today = date.today()
                return today.year - born.year - ((today.month, today.day) <
                                                 (born.month, born.day))

            if record.birthday:
                record.age = calculate_age(
                    fields.Datetime.from_string(record.birthday))

    # hereda domicilio de atención
    inherit_address = fields.Boolean("Usar dirección de la empresa?")

    # enfermedades previas
    prev_ailments = fields.Text("Previous Ailments")

    # alergias
    allergies = fields.Text("Allergies")

    # estatus
    user_active = fields.Boolean("Active")

    # fecha de registro
    start_date = fields.Date("Registration Date")

    # fecha cuando se dio de baja
    end_date = fields.Date("Date Ended")

    # fecha de baja automatica
    auto_end_date = fields.Date("End Date")

    # motivo de baja
    end_reason = fields.Text("Reason for Ending")

    # dar de baja usuarios con fecha de baja
    def _user_end_date(self):
        # juntar cápitas y afiliados en un solo query
        self.env.cr.execute("""
            SELECT id,'family' as member_type,user_active,start_date,auto_end_date
            FROM family_member
            UNION ALL
            SELECT id,'company' as member_type,user_active,start_date,auto_end_date
            FROM company_member;
        """)

        # iterar por resultados del query
        for member in self.env.cr.dictfetchall():
            is_active = member['user_active']
            end_date = member['auto_end_date']
            has_ended = fields.Datetime.from_string(
                end_date) < datetime.now() if end_date else False

            # si es un miembro activo cuya fecha final se excedio
            if is_active and has_ended:
                id = member['id']
                model = member['member_type'] + ".member"
                current = self.env[model].browse(id)

                _logger.info('crontab _user_end_date')

                # desactivar el usuario y poner fecha final de hoy
                current.write({
                    'end_date': fields.Date.today(),
                    'auto_end_date': None,
                    'user_active': False,
                    'end_reason': 'Baja automática',
                })

                # guardar cambios en la base de datos
                self.env.cr.commit()


class FamilyMember(models.Model):
    _name = "family.member"
    _inherit = "user.member"

    # grupos del cual miembro es titular
    main_contact = fields.One2many(
        "res.partner", "family_contact_id", string="Main Contact")

    # condición de grupo
    relationship = fields.Selection(
        string="Relationship",
        selection=[("1", odoo._("Father")), ("2", odoo._("Mother")),
                   ("3", odoo._("Spouse")), ("4", odoo._("Offspring")),
                   ("5", odoo._("Other family"))])

    # comenzar suscripción
    @api.multi
    def start_reg(self):
        for record in self:
            record.start_date = fields.Datetime.to_string(datetime.now())
            record.end_date = ""
            record.user_active = True

    # terminar suscripción
    @api.multi
    def end_reg(self):
        for record in self:
            record.end_date = fields.Datetime.to_string(datetime.now())
            record.auto_end_date = ""
            record.user_active = False


class CompanyMember(models.Model):
    _name = "company.member"
    _inherit = "user.member"

    # grupos del cual miembro es titular
    main_contact = fields.One2many(
        "res.partner", "company_contact_id", string="Main Contact")

    # condición de grupo
    relationship = fields.Selection(
        string="Role",
        selection=[("1", odoo._("Owner")), ("2", odoo._("Director")),
                   ("3", odoo._("Executive")), ("4", odoo._("Administrator")),
                   ("5", odoo._("Employee")), ("6", odoo._("Other"))])

    # comenzar suscripción
    @api.multi
    def start_reg(self):
        for record in self:
            record.start_date = fields.Datetime.to_string(datetime.now())
            record.end_date = ""
            record.user_active = True

    # terminar suscripción
    @api.multi
    def end_reg(self):
        for record in self:
            record.end_date = fields.Datetime.to_string(datetime.now())
            record.auto_end_date = ""
            record.user_active = False
