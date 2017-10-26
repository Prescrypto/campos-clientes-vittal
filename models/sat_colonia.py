# -*- coding: utf-8 -*-

from odoo import models, fields


class SatColonia(models.Model):
    _name = "sat.colonia"

    _rec_name = "nombre_colonia"

    nombre_colonia = fields.Char(string="Nombre del asentamiento")

    codigo_colonia = fields.Char(string="Código de colonia")

    codigo_postal = fields.Char(string="Código de colonia")

    sat_colonia_ids = fields.One2many(
        "res.partner", "sat_colonia_id", string="Colonias")
