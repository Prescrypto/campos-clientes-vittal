# -*- coding: utf-8 -*-

from odoo import models, fields, api

class campos_clientes_vittal(models.Model):
    _inherit = 'res.partner'

    zip_extra = fields.Char(string="Zip Extra", help="Extended Zip code")
