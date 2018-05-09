# -*- coding: utf-8 -*-
import _sae as sae
from functools import partial
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

    # direccion de factura de orden de venta
    invoice_address = fields.One2many(
        "sale.order", "invoice_address_id", string="Dirección de factura")

    # correo derivado de dirección fiscal
    invoice_email = fields.Char(
        "Correo de factura", compute="_invoice_email", store=True)

    @api.one
    @api.depends('child_ids')
    def _invoice_email(self):
        for child in self.child_ids:
            if child.type == 'fiscal':
                self.invoice_email = child.email

    # direccion de cobertura de orden de venta
    cov_address = fields.One2many(
        "sale.order", "cov_address_id", string="Dirección de cobertura")

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
    sat_pagos_id = fields.Many2one("sat.pagos", "Forma de Pago")

    # metodos de pago
    sat_metodo_pago = fields.Selection([
            ('PUE', 'PUE - PAGO EN UNA SOLA EXHIBICIÓN'),
            ('PPD', 'PPD - PAGO EN PARCIALIDADES O DIFERIDO')
        ], 'Método de Pago', default='PUE')

    # codigo derivado de forma de pago
    sat_pagos_codigo = fields.Char(
        related="sat_pagos_id.codigo_forma", store=True)

    # tipos de dirección
    type = fields.Selection(
        string="Tipo de domicilio",
        selection=[("contact", "Contacto"),
                   ("coverage", "Domicilio de cobertura"),
                   ("admin", "Domicilio Administrativo"),
                   ("fiscal", "Domicilio Fiscal")])
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
                'type': 'coverage',
                'zone': partner.zone,
                'cross_street': partner.cross_street,
                'crosses_with': partner.crosses_with,
                'references': partner.references,
                'exterior': partner.exterior,
                'details': partner.details
            }
            self.create(new_vals)
        return partner

    # exportación sae
    export_columns = [
        'client_export_id',
        'name',
        'rfc',
        'street',
        'street2',
        'cross_street',
        'crosses_with',
        'sat_colonia_id',
        'zip',
        'poblacion',
        'sat_municipio_id',
        'sat_estado_id',
        'sat_pais_id',
        'nacionalidad',
        'reference_id',
        'phone',
        'fax',
        'website',
        'curp',
        'invoice_email',
        'sat_uso_codigo',
        'sat_pagos_codigo',
        'zone',
    ]

    @api.multi
    def export(self):
        columns = self.export_columns
        format_clients = partial(sae.format, 'clients')
        return map(format_clients, self.export_data(columns).get('datas', []))

    def export_all(self):
        all_clients = self.env['res.partner']
        valid_clients = all_clients.search([['active', '=', True], ['customer', '=', True], ['parent_id', '=', False]])

        columns = self.export_columns
        format_clients = partial(sae.format, 'clients')

        return map(format_clients, valid_clients.export_data(columns).get('datas', []))

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
