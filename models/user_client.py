# -*- coding: utf-8 -*-

import string
from odoo import models, fields, api, _


class user_client(models.Model):
    _inherit = "res.partner"

    parent_group_ids = fields.Many2many(
        comodel_name="res.partner",
        relation="client_related_entities_rel",
        column1="parent_id",
        column2="child_id",
        string="Parents")

    child_group_ids = fields.Many2many(
        comodel_name="res.partner",
        relation="client_related_entities_rel",
        column1="child_id",
        column2="parent_id",
        string="Children")

    # titular familiar
    family_contact_id = fields.Many2one("family.member", string="Main Contact")

    # miembros de clientes que usan la direccion para domicilio de atención
    family_atte_address = fields.One2many(
        "family.member", "atte_address_id", string="Attention Address")

    company_atte_address = fields.One2many(
        "company.member", "atte_address_id", string="Attention Address")

    # direccion de factura de orden de venta
    invoice_address = fields.One2many(
        "sale.order", "invoice_address_id", string="Invoice Address")

    # direccion de cobertura de orden de venta
    cov_address = fields.One2many(
        "sale.order", "cov_address_id", string="Coverage Address")

    # titular empresarial
    company_contact_id = fields.Many2one(
        "company.member", string="Main Contact")

    # cambiar formato de nombre de titular
    def name_get(self):
        res = []
        for record in self:
            if record.type != 'contact':
                tpl = string.Template("$street, $street2$city")
                label = tpl.substitute(
                    street=record.street,
                    street2=(record.street2 + ", " if record.street2 else ""),
                    city=record.city)
                res.append((record.id, label))
            else:
                res.append((record.id, record.name))
        return res

    # codigo de grupo
    group_code = fields.Char("Group Code", compute="_group_code", store=True)

    @api.multi
    @api.depends("client_type")
    def _group_code(self):
        for record in self:
            if record.client_type:
                prefix = {
                    "company": "E",
                    "family": "F",
                    "private": "P",
                }[record.client_type]
                record.group_code = prefix + str(record.id)

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

    # tipo de negocio
    business_type = fields.Char("Business Type")

    # código de zona
    zone = fields.Selection(
        string="Zone",
        selection=[("bqelms", "BQELMS"), ("itrlms", "ITRLMS"),
                   ("lomas", "LOMAS"), ("plnco", "PLNCO"), ("sfe", "SFE"),
                   ("tcmchl", "TCMCHL"), ("unica", "UNICA")])

    # tipos de dirección
    type = fields.Selection(
        string="Address Type",
        selection=[("contact", _("Contact")), ("coverage",
                                               _("Coverage Address")),
                   ("admin", _("Administrative Address")),
                   ("fiscal", _("Fiscal Address"))])

    # entre calles
    cross_street = fields.Char("Cross Streets")

    # referencias
    references = fields.Char("References")

    # fachada
    exterior = fields.Char("Exterior")

    # características especiales
    details = fields.Char("Details")

    # exportación sae
    @api.multi
    def export_order(self):
        columns = [
            'id',
        ]
        return self.export_data(columns).get('datas', [])
