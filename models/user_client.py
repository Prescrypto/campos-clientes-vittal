# -*- coding: utf-8 -*-
import _sae as sae
from functools import partial
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

    # direccion de factura de orden de venta
    invoice_address = fields.One2many(
        "sale.order", "invoice_address_id", string="Invoice Address")

    # correo derivado de dirección fiscal
    invoice_email = fields.Char(
        "Invoice Email", compute="_invoice_email", store=True)

    @api.one
    @api.depends('child_ids')
    def _invoice_email(self):
        for child in self.child_ids:
            if child.type == 'fiscal':
                self.invoice_email = child.email

    # direccion de cobertura de orden de venta
    cov_address = fields.One2many(
        "sale.order", "cov_address_id", string="Coverage Address")

    # titular empresarial
    company_contact_id = fields.Many2one(
        "company.member", string="Main Contact")

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

    # tipo de usuario adicional
    client_type = fields.Selection(selection=[("company", _("Company")), (
        "family", _("Family")), ("private", _("Private"))])

    # nombre comercial
    legal_name = fields.Char("Legal Name")

    # rfc
    rfc = fields.Char("RFC")

    # tipo de negocio
    business_type = fields.Char("Business Type")

    # código de zona
    zone = fields.Selection(
        string="Zone",
        selection=[("bqelms", "BQELMS - Bosques de las Lomas"),
                   ("itrlms", "ITRLMS - Interlomas"),
                   ("lomas", "LOMAS - Lomas de Chapultepec"),
                   ("plnco", "PLNCO - Polanco"),
                   ("sfe", "SFE - Santa Fe"),
                   ("tcmchl", "TCMCHL - Tecamachalco"),
                   ("unica", "UNICA - Fuera de Zona de Cobertura")])

    # catalogo de colonias
    sat_colonia_id = fields.Many2one("sat.colonia", "Colonia")

    # catalogo de municipios
    sat_municipio_id = fields.Many2one("sat.municipio", "Municipio")

    # nombre derivado de catalogo de municipio
    sat_municipio_name = fields.Char(
        related="sat_municipio_id.nombre_municipio", store=True)

    # catalogo de colonias
    sat_estado_id = fields.Many2one("sat.estado", "Estado")

    # catalogo de paises
    sat_pais_id = fields.Many2one("sat.pais", "País")

    # catalogo de usos de cfdi
    sat_uso_id = fields.Many2one("sat.uso", "Uso CFDI")

    # codigo derivado de uso de cfdi
    sat_uso_codigo = fields.Char(related="sat_uso_id.codigo_uso", store=True)

    # catalog de formas de pago
    sat_pagos_id = fields.Many2one("sat.pagos", "Formas de Pago")

    # codigo derivado de forma de pago
    sat_pagos_codigo = fields.Char(
        related="sat_pagos_id.codigo_forma", store=True)

    # tipos de dirección
    type = fields.Selection(
        string="Address Type",
        selection=[("contact", _("Contact")), ("coverage",
                                               _("Coverage Address")),
                   ("admin", _("Administrative Address")),
                   ("fiscal", _("Fiscal Address"))])

    # entre calles
    cross_street = fields.Char("Cross Street")

    # y calle
    crosses_with = fields.Char("Crosses With")

    # referencias
    references = fields.Char("References")

    # fachada
    exterior = fields.Char("Exterior")

    # características especiales
    details = fields.Char("Details")

    # número de referencia
    reference_id = fields.Char("Reference Number")

    # CURP
    curp = fields.Char("CURP")

    # población
    poblacion = fields.Char("Población")

    # nacionalidad
    nacionalidad = fields.Char("Nacionalidad")

    # id externo en tabla de res_partner
    client_export_id = fields.Char("Export ID", default="None")
    
    def name_get(self):
        ''' Cambiar formato de nombre de titular y direcciones '''
        result = []
        for record in self:
            if record.name:
                result.append((record.id, record.name))
            else:
                label = u"{}{}".format(
                    record.street,
                    (", " + record.street2 if record.street2 else ""))
                result.append((record.id, label ))
        return result
