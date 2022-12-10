# -*- coding: utf-8 -*-

from odoo import models, fields, api


_logger = logging.getLogger(__name__)



class Invoice(models.Model):
    _inherit = 'account.invoice'

    #################################
    # CAMPOS CFDI

    sat_uso_id = fields.Many2one("sat.uso", "Uso CFDI")
    sat_pagos_id = fields.Many2one("sat.pagos", "Forma de Pago")
    sat_metodo_pago = fields.Selection([
        ('PUE', 'PUE - PAGO EN UNA SOLA EXHIBICION'),
            ('PPD', 'PPD - PAGO EN PARCIALIDADES O DIFERIDO')
    ], 'Método de Pago')
    sat_pegaso_request = fields.Text("Pegaso Request")
    sat_pegaso_response = fields.Text("Pegaso Response")
    sat_pegaso_ok = user_active = fields.Boolean("Timbrado")
    #################################

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        self.sat_uso_id = self.partner_id.fiscal_address.sat_uso_id
        self.sat_metodo_pago = self.partner_id.fiscal_address.sat_metodo_pago
        self.sat_pagos_id = self.partner_id.fiscal_address.sat_pagos_id

    @api.one
    def action_invoice_cfdi(self):
        _logger.debug('send message to debug')
        _logger.info('send message to info')
        self.write({'sat_pegaso_request': ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(randint(9,15)))})
        #self.sat_pegaso_request = self.sat_pegaso_request + "TEst"
        return True
