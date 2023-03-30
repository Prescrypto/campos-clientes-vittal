# -*- coding: utf-8 -*-

from odoo import models, fields


class SatRegimen(models.Model):
    _name = "sat.regimen"

    _rec_name = "nombre_regimen"

    codigo_regimen = fields.Char("Código de regimen")

    nombre_regimen = fields.Char("Nombre del regimen")

    sat_regimen_ids = fields.One2many(
        "res.partner", "sat_regimen_id", string="Regimen Fiscal")
