# -*- coding: utf-8 -*-

import odoo
from odoo import models, fields, api


class user_client(models.Model):
    _inherit = "res.partner"

    # direcciones del grupo
    address_ids = fields.One2many(
        "partner.address", "parent_id", string="Addresses")

    # miembros del grupo
    member_ids = fields.One2many(
        "partner.member", "parent_id", string="Members")

    # código de grupo
    group_id = fields.Selection(
        string="Group Code",
        selection=[("area_p", "AREA-P"), ("conv", "CONV"),
                   ("evento", "EVENTO"), ("grupos", "GRUPOS"), ("otros",
                                                                "OTROS")])

    group_name = fields.Char(compute="_group_name", store=True)

    @api.depends("group_id")
    def _group_name(self):
        for record in self:
            if record.group_id:
                record.group_name = {
                    "area_p": odoo._("Protected Areas"),
                    "conv": odoo._("Agreements"),
                    "evento": odoo._("Events"),
                    "grupos": odoo._("Groups"),
                    "otros": odoo._("Other")
                }.get(record.group_id, odoo._("None Selected"))

    # código postal de colonia
    zip_extra = fields.Char("Zip Extra")

    # tipo de usuario adicional
    client_type = fields.Selection(selection=[("company", "Company"),
                                              ("family", "Family"),
                                              ("individual", "Individual")])

    # nombre comercial
    legal_name = fields.Char("Legal Name")

    # rfc
    rfc = fields.Char("RFC")

    # lada de país
    country_code = fields.Char("Country Code")

    # código de zona
    zone = fields.Selection(
        string="Zone",
        selection=[("bqelms", "BQELMS"), ("itrlms", "ITRLMS"),
                   ("lomas", "LOMAS"), ("plnco", "PLNCO"), ("sfe", "SFE"),
                   ("tcmchl", "TCMCHL"), ("unica", "UNICA")])

    # código de producto
    product_custom_id = fields.Char("Product Code")

    # cápitas
    quantity = fields.Integer("Quantity")

    # hogar protegido
    protected_home_auto = fields.Boolean(
        compute="_protected_home_auto", store=True, readonly=True)

    @api.depends("quantity")
    def _protected_home_auto(self):
        for record in self:
            if record.quantity > 4:
                record.protected_home_auto = True

    protected_home_user = fields.Boolean("Protected Home")

    protected_home = fields.Boolean(compute="_protected_home", store=True)

    @api.depends("protected_home_auto", "protected_home_user")
    def _protected_home(self):
        for record in self:
            if record.protected_home_auto or record.protected_home_user:
                record.protected_home = True
