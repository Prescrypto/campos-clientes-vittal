# -*- coding: utf-8 -*-

from odoo import models, fields, api

#CFDI 
import logging
from datetime import datetime
import pytz
from lxml import etree
import xml.etree.ElementTree as ET

_logger = logging.getLogger(__name__)

#
BASE_XML="""
<?xml version="1.0" encoding="UTF-8"?><soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:scfd="http://namespace.pegasotecnologia.com/SCFD" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/">
    <soapenv:Header></soapenv:Header>
    <soapenv:Body>
        <scfd:emitirCFD>
            <scfd:PoRequestCFD>{}</scfd:PoRequestCFD>
        </scfd:emitirCFD>
    </soapenv:Body>
</soapenv:Envelope>"""

EMISOR_RFC = 'TMO1104114Y9'
EMISOR_NOMBRE = 'TIEMPOREAL_TMO1104114Y9_ws'
EMISOR_REGIMENFISCAL = '612'
EMISOR_LUGAR = '15900'
TIMEOUT_TOLERANCE = 25
HEADER_SOAPACTION="http://namespace.pegasotecnologia.com/SCFD/IEmisionBaseExternalService/emitirCFD"
REQUEST_URL = "https://qa.pegasotecnologia.mx/ServAdmEmisionGatewayQA/ServiceGateway.svc/Soap11Text"


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

    @api.multi
    def action_invoice_open(self):
        # lots of duplicate calls to action_invoice_open, so we remove those already open
        to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
        if to_open_invoices.filtered(lambda inv: inv.state not in ['proforma2', 'draft']):
            raise UserError(_("Invoice must be in draft or Pro-forma state in order to validate it."))
        to_open_invoices.action_date_assign()
        to_open_invoices.action_move_create()
        return to_open_invoices.invoice_validate()


    @api.one
    def action_invoice_cfdi(self):
        invoice_id = self.number.split("/")

        client_dict = {'customer_name': self.partner_id.name,
         'date': self.date_invoice,
         'customer_rfc': self.partner_id.rfc,
         'customer_payment_id': self.sat_pagos_id.codigo_forma,
         'customer_payment_name': self.sat_pagos_id.nombre_forma,
         'customer_payment_use_id': self.sat_uso_id.codigo_uso,
         'customer_payment_use_name': self.sat_uso_id.nombre_uso,
         'customer_email': self.partner_id.email,
         'invoice_id': self.number,
         'invoice_series': invoice_id[0],
         'invoice_folio': invoice_id[1]+invoice_id[2] 
         }
        _logger.debug('send message to debug')
        _logger.debug("self:{}".format(self))
        _logger.info('send message to info')

        self.write({'sat_pegaso_request': client_dict })
        #self.sat_pegaso_request = self.sat_pegaso_request + "TEst"
        return True
    @api.one
    def action_cfdi_paremeters(self):
        utcmoment_naive = datetime.utcnow()
        utcmoment = utcmoment_naive.replace(tzinfo=pytz.utc)
        satLocalFormat = "%Y-%m-%dT%H:%M:%S"
        satTimeZone = 'America/Mexico_City'
        localDatetime = utcmoment.astimezone(pytz.timezone(satTimeZone))
        satDateCFDI = localDatetime.strftime(satLocalFormat)
        return satDateCFDI