# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Invoice(models.Model):
    _inherit = 'account.invoice'

    #################################
    # CAMPOS CFDI

    sat_uso_id = fields.Many2one("sat.uso", "Uso CFDI")
    sat_pagos_id = fields.Many2one("sat.pagos", "Forma de Pago")
    sat_metodo_pago = fields.Selection([
        ('PUE - PAGO EN UNA SOLA EXHIBICION', 'PUE - PAGO EN UNA SOLA EXHIBICIÓN'),
        ('PPD - PAGO EN PARCIALIDADES O DIFERIDO', 'PPD - PAGO EN PARCIALIDADES O DIFERIDO')
    ], 'Método de Pago')

    #################################

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        self.sat_uso_id = self.partner_id.fiscal_address.sat_uso_id
        self.sat_metodo_pago = self.partner_id.fiscal_address.sat_metodo_pago
        self.sat_pagos_id = self.partner_id.fiscal_address.sat_pagos_id
