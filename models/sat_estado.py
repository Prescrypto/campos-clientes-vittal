# -*- coding: utf-8 -*-

from odoo import models, fields


class SatEstado(models.Model):
    _name = "sat.estado"

    _rec_name = "nombre_estado"

    nombre_estado = fields.Char("Nombre del estado")

    codigo_estado = fields.Char("Código de estado")

    codigo_pais = fields.Char("Código de pais")

    sat_estado_ids = fields.One2many(
        "res.partner", "sat_estado_id", string="Estados")
