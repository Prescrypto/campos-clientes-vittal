# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class user_client(models.Model):
    _inherit = "res.partner"

    # titular
    main_contact = fields.Char("Main Contact")

    # codigo de grupo
    group_code = fields.Char("Group Code", compute="_group_code", store=True)

    @api.one
    @api.depends("client_type")
    def _group_code(self):
        if self.client_type and self.id:
            prefix = {
                "company": "E",
                "family": "F",
                "private": "P",
            }[self.client_type]
            self.group_code = prefix + str(self.id)

    # direcciones del grupo
    address_ids = fields.One2many(
        "partner.address", "parent_id", string="Addresses")

    # miembros del grupo
    family_ids = fields.One2many(
        "family.member", "parent_id", string="Family Members")

    # miembros del grupo
    company_ids = fields.One2many(
        "company.member", "parent_id", string="Company Members")

    # código postal de colonia
    zip_extra = fields.Char("Zip Extra")

    # tipo de usuario adicional
    client_type = fields.Selection(selection=[("company", _("Company")),
                                              ("family", _("Family")),
                                              ("private", _("Private"))])

    # nombre comercial
    legal_name = fields.Char("Legal Name")

    # rfc
    rfc = fields.Char("RFC")

    # código de zona
    zone = fields.Selection(
        string="Zone",
        selection=[("bqelms", "BQELMS"), ("itrlms", "ITRLMS"),
                   ("lomas", "LOMAS"), ("plnco", "PLNCO"), ("sfe", "SFE"),
                   ("tcmchl", "TCMCHL"), ("unica", "UNICA")])
