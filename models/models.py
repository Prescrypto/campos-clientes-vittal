# -*- coding: utf-8 -*-

from odoo import models, fields, api

class campos_clientes_vittal(models.Model):
    _inherit = 'res.partner'

    zip_extra = fields.Char(string="Zip Extra", help="Extended zip code")

    # fn ex
    #
    # value = fields.Integer()
    # value2 = fields.Float(compute="_value_pc", store=True)
    #
    # @api.depends('value')
    # def _value_pc(self):
    #     self.value2 = float(self.value) / 100
