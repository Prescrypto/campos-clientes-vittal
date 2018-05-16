# -*- coding: utf-8 -*-

from odoo import models, fields


class SatPais(models.Model):
    _name = "sat.pais"

    _rec_name = "nombre_pais"

    codigo_pais = fields.Char("Código de País")

    nombre_pais = fields.Char("Nombre de País")

    formato_codigo_postal = fields.Char("Formato de Código Postal")

    formato_registro = fields.Char(
        "Formato de Registro de Identidad Tributaria")

    validacion_registro = fields.Char(
        "Validación del Registro de Identidad Tributaria")

    agrupaciones = fields.Char("Agrupaciones")

    sat_pais_ids = fields.One2many("res.partner", "sat_pais_id", string="País")
