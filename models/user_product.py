# -*- coding: utf-8 -*-

import odoo
import _sae as sae
from functools import partial
from odoo import models, fields, api


class user_product(models.Model):
    _inherit = "product.template"

    # filtro de suscripcion
    type = fields.Selection(selection_add=[("sub", odoo._("Subscription"))])

    # tipo de elemento
    tipo_elemento = fields.Char(
        "Tipo de Elemento", compute="_element_type", store=True)

    @api.depends("type")
    def _element_type(self):
        for record in self:
            if record.type:
                prefix = {
                    "sub": "S",
                    "service": "S",
                    "consu": "P",
                }[record.type]
                record.tipo_elemento = prefix
            else:
                record.tipo_elemento = "P"

    # clave erste
    clave_erste = fields.Char("Clave ERSTE")

    # cuenta contable
    cuenta_contable = fields.Char("Cuenta Contable", size=28)

    # clave sat
    clave_sat = fields.Selection(
        string="Clave SAT",
        selection=[("85121502", "Consultas médicas de medicina general"),
                   ("85101507", "Centros asistenciales de urgencia"),
                   ("85101508",
                    "Centros o servicios móviles de atención de salud"),
                   ("85121800", "Laboratorios médicos"),
                   ("85121502",
                    "Servicios de consulta de médicos de atención primeria"),
                   ("85121600",
                    "Servicios médicos de doctores especialistas")])

    codigo_sat = fields.Char("Código SAT", compute="_get_id", store=True)

    @api.depends("clave_sat")
    def _get_id(self):
        for record in self:
            if record.clave_sat:
                record.codigo_sat = record.clave_sat

    # clave de unidad
    clave_unidad = fields.Char(
        "Clave Unidad", compute="_get_group", store=True)

    @api.depends("clave_sat")
    def _get_group(self):
        for record in self:
            if record.clave_sat:
                prefix = {
                    "85121502": "E48",
                    "85101507": "E48",
                    "85101508": "E48",
                    "85121800": "E48",
                    "85121502": "E48",
                    "85121600": "E48",
                }[record.clave_sat]
                record.clave_unidad = prefix

    # exportación sae
    export_columns = [
        "id",
        "description_sale",
        "tipo_elemento",
        "cuenta_contable",
        "codigo_sat",
        "clave_unidad",
        "clave_erste",
    ]

    def export(self):
        columns = self.export_columns
        format_products = partial(sae.format, "products")
        return map(format_products, self.export_data(columns).get("datas", []))

    def export_all(self):
        all_products = self.env['product.template']
        valid_products = all_products.search([])

        columns = self.export_columns
        format_products = partial(sae.format, "products")

        return map(format_products, valid_products.export_data(columns).get('datas', []))
