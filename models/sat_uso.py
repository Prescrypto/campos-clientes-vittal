# -*- coding: utf-8 -*-

from odoo import models, fields


class SatUso(models.Model):
    _name = "sat.uso"

    _rec_name = "nombre_uso"

    codigo_uso = fields.Char("Código de País")

    nombre_uso = fields.Char("Nombre de País")

    aplica_fisica = fields.Boolean("Aplica a Persona Física")

    aplica_moral = fields.Boolean("Aplica a Persona Moral")

    inicio_vigencia = fields.Date("Inicio de Vigencia")

    fin_vigencia = fields.Date("Fin de Vigencia")

    sat_uso_ids = fields.One2many(
        "res.partner", "sat_uso_id", string="Uso CFDI")
