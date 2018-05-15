# -*- coding: utf-8 -*-

from odoo import models, fields


class SatUso(models.Model):
    _name = "sat.uso"

    _rec_name = "nombre_uso"

    codigo_uso = fields.Char("Código SAT")

    nombre_uso = fields.Char("Nombre")

    aplica_fisica = fields.Boolean("Aplica a Persona Física")

    aplica_moral = fields.Boolean("Aplica a Persona Moral")

    inicio_vigencia = fields.Date("Inicio de Vigencia")

    sat_uso_ids = fields.One2many(
        "res.partner", "sat_uso_id", string="Uso CFDI")
