# -*- coding: utf-8 -*-

from odoo import models, fields, api

class campos_clientes_vittal(models.Model):
    _inherit = 'res.partner'

    # codigo postal de colonia
    zip_extra = fields.Char(string="Zip Extra", help="Extended zip code")

    # agregar tipo de usuario adicional
    client_type = fields.Selection(selection=[
        ('company', 'Company'),
        ('family', 'Family'),
        ('individual', 'Individual')])

    # agregar nombre comercial
    legal_name = fields.Char(string="Legal Name", help="Legal or fiscal name of business")

    # fn ex
    #
    # value = fields.Integer()
    # value2 = fields.Float(compute="_value_pc", store=True)
    #
    # @api.depends('value')
    # def _value_pc(self):
    #     self.value2 = float(self.value) / 100
