# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class user_client(models.Model):
    _inherit = "res.partner"

    parent_group_ids = fields.Many2many(
        comodel_name="res.partner",
        relation="client_related_entities_rel",
        column1="parent_id",
        column2="child_id",
        domain="['&',('customer','=',True),('id','!=',id)]",
        string="Parents")

    child_group_ids = fields.Many2many(
        comodel_name="res.partner",
        relation="client_related_entities_rel",
        column1="child_id",
        column2="parent_id",
        domain="['&',('customer','=',True),('id','!=',id)]",
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
    @api.multi
    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, record.name))
        return result

    # codigo de grupo
    group_code = fields.Char("Group Code", compute="_group_code", store=True)

    @api.one
    @api.depends("client_type")
    def _group_code(self):
        if self.client_type:
            prefix = {
                "company": "E",
                "family": "F",
                "private": "P",
            }[self.client_type]
            self.group_code = prefix + str(self.id)

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
        selection=[("contact", _("Contact")),
                   ("coverage", _("Coverage Address")),
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
