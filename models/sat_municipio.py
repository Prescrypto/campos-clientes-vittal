# -*- coding: utf-8 -*-

from odoo import models, fields


class SatMunicipio(models.Model):
    _name = "sat.municipio"

    _rec_name = "nombre_municipio"

    codigo_municipio = fields.Char("Código de Municipio")

    nombre_municipio = fields.Char("Nombre de Municipio")

    codigo_estado = fields.Char("Código de Estado")

    sat_municipio_ids = fields.One2many(
        "res.partner", "sat_municipio_id", string="País")
