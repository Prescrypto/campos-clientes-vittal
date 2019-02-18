# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning


class UserClient(models.Model):
    _inherit = "res.partner"

    parent_group_ids = fields.Many2many(
        comodel_name="res.partner",
        relation="client_related_entities_rel",
        column1="parent_id",
        column2="child_id",
        string="Padres")

    child_group_ids = fields.Many2many(
        comodel_name="res.partner",
        relation="client_related_entities_rel",
        column1="child_id",
        column2="parent_id",
        string="Descendientes")

    # titular familiar
    family_contact_id = fields.Many2one("family.member", string="Titular")

    # titular empresarial
    company_contact_id = fields.Many2one(
        "company.member", string="Titular")

    # codigo de grupo
    group_code = fields.Char("Código de grupo", compute="_group_code", store=True)

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
        "family.member", "parent_id", string="Miembros de familia")

    # miembros del grupo
    company_ids = fields.One2many(
        "company.member", "parent_id", string="Miembros de empresa")

    # tipo de usuario adicional
    client_type = fields.Selection(selection=[("company", "Empresa"),
                                              ("family", "Familia"),
                                              ("private", "Privado")], string="Tipo de cliente")

    # nombre comercial
    legal_name = fields.Char("Nombre comercial")

    # rfc
    rfc = fields.Char("RFC")

    # tipo de negocio
    business_type = fields.Many2one("business.type", "Tipo de negocio")

    # código de zona
    zone = fields.Selection(
        string="Zona",
        selection=[("BQELMS - Bosques de las Lomas", "BQELMS - Bosques de las Lomas"),
                   ("ITRLMS - Interlomas", "ITRLMS - Interlomas"),
                   ("LOMAS - Lomas de Chapultepec", "LOMAS - Lomas de Chapultepec"),
                   ("PLNCO - Polanco", "PLNCO - Polanco"),
                   ("SFE - Santa Fe", "SFE - Santa Fe"),
                   ("TCMCHL - Tecamachalco", "TCMCHL - Tecamachalco"),
                   ("UNICA - Fuera de Zona de Cobertura", "UNICA - Fuera de Zona de Cobertura")])

    # catalogo de colonias
    sat_colonia_id = fields.Many2one("sat.colonia", "Colonia")

    # catalogo de municipios
    sat_municipio_id = fields.Many2one("sat.municipio", "Municipio")

    # catalogo de colonias
    sat_estado_id = fields.Many2one("sat.estado", "Estado")

    # catalogo de paises
    sat_pais_id = fields.Many2one("sat.pais", "País")

    # catalogo de usos de cfdi
    sat_uso_id = fields.Many2one("sat.uso", "Uso CFDI")

    # catalog de formas de pago
    sat_pagos_id = fields.Many2one("sat.pagos", "Forma de Pago")

    # metodos de pago
    sat_metodo_pago = fields.Selection([
            ('PUE - PAGO EN UNA SOLA EXHIBICION', 'PUE - PAGO EN UNA SOLA EXHIBICION'),
            ('PPD - PAGO EN PARCIALIDADES O DIFERIDO', 'PPD - PAGO EN PARCIALIDADES O DIFERIDO')
        ], 'Método de Pago')

    # Número de cuenta

    account_number = fields.Char('Número de cuenta')

    # tipos de dirección
    type = fields.Selection(
        string="Tipo de domicilio",
        selection=[("contact", "Contacto"),
                   ("coverage", "Domicilio de cobertura"),
                   ("admin", "Domicilio Administrativo"),
                   ("fiscal", "Domicilio Fiscal")])

    # Marcar si la dirección fiscal es la principal
    main_fiscal_address = fields.Boolean('Dirección fiscal principal', default=False)

    # Copago
    copago = fields.Boolean('Copago')
    # monto copago
    copago_amount = fields.Float('Monto Copago')

    # entre calles
    cross_street = fields.Char("Entre calles")

    # y calle
    crosses_with = fields.Char("Y calle")

    # referencias
    references = fields.Char("Referencias")

    # fachada
    exterior = fields.Char("Fachada")

    # características especiales
    details = fields.Char("Características especiales")

    # número de referencia
    reference_id = fields.Char("ID Erste")

    # CURP
    curp = fields.Char("CURP")

    # población
    poblacion = fields.Char("Población")

    # nacionalidad
    nacionalidad = fields.Char("Nacionalidad")

    # id externo en tabla de res_partner
    client_export_id = fields.Char("Export ID", default="None")

    # Dirección fiscal principal, en caso de no tener se pone el propio partner
    fiscal_address = fields.Many2one('res.partner', 'Dirección Fiscal', compute="_get_fiscal_address", store=False)

    # Facturas pendientes de pago
    outstanding = fields.Boolean('Factura pendiente de pago', compute="_get_outstanding", store=False)

    # Calcular dirección
    @api.one
    def _get_fiscal_address(self):
        for p in self.child_ids:
            if p.main_fiscal_address:
                self.fiscal_address = p
                return
        self.fiscal_address = self

    # Calcular si faltan facturas de pagar
    @api.one
    def _get_outstanding(self):
        invoices = self.env['account.invoice'].sudo().search([('partner_id', 'in', [self.id]), ('state', 'not in', ['paid', 'cancel'])])
        contract = self.env['account.analytic.account'].sudo().search([('partner_id', 'in', [self.id])])
        self.outstanding = len(invoices) > 0 or len(contract) == 0

    @api.multi
    def write(self, vals):
        result = super(UserClient, self).write(vals)
        for p in self:
            if p.parent_id and p.main_fiscal_address:
                super(UserClient, p.parent_id.child_ids).write({'main_fiscal_address': False})
                super(UserClient, p).write({'main_fiscal_address': True})
        return result

    @api.model
    def create(self, vals):
        partner = super(UserClient, self).create(vals)
        if not partner.parent_id:
            new_vals = {
                'parent_id': partner.id,
                'name': partner.name,
                'street': partner.street,
                'street2': partner.street2,
                'sat_municipio_id': partner.sat_municipio_id.id,
                'sat_estado_id': partner.sat_estado_id.id,
                'zip': partner.zip,
                'sat_colonia_id': partner.sat_colonia_id.id,
                'sat_pais_id': partner.sat_pais_id.id,
                'phone': partner.phone,
                'mobile': partner.mobile,
                'email': partner.email,
                'type': 'coverage',
                'zone': partner.zone,
                'cross_street': partner.cross_street,
                'crosses_with': partner.crosses_with,
                'references': partner.references,
                'exterior': partner.exterior,
                'details': partner.details,
                'customer': False
            }
            self.create(new_vals)
        elif partner.main_fiscal_address:
            partner.write({'main_fiscal_address': True})
        return partner

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
