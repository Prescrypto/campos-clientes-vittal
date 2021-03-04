# -*- coding: utf-8 -*-

from odoo import models, fields, api

#CFDI 
import logging
from datetime import datetime
import pytz
from lxml import etree
import xml.etree.ElementTree as ET

import RequestCFD_v33 as api_cfdi
import requests
import os
import traceback
#import xmltodict, json

_logger = logging.getLogger(__name__)


BASE_XML="""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:scfd="http://namespace.pegasotecnologia.com/SCFD" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/">
    <soapenv:Header></soapenv:Header>
    <soapenv:Body>
        <scfd:emitirCFD>
            <scfd:PoRequestCFD>
            {}
            </scfd:PoRequestCFD>
        </scfd:emitirCFD>
    </soapenv:Body>
</soapenv:Envelope>"""


EMISOR_RFC = os.environ['EMISOR_RFC']
EMISOR_NOMBRE = os.environ['EMISOR_NOMBRE']
EMISOR_REGIMENFISCAL = os.environ['EMISOR_REGIMENFISCAL']
EMISOR_LUGAR = os.environ['EMISOR_LUGAR']
TIMEOUT_TOLERANCE = os.environ['TIMEOUT_TOLERANCE']
HEADER_SOAPACTION = os.environ['HEADER_SOAPACTION']
REQUEST_URL = os.environ['REQUEST_URL']
TEMPORAL_OUT_XML = os.environ['TEMPORAL_OUT_XML']
TEMPORAL_OUT_XML_OK = os.environ['TEMPORAL_OUT_XML_OK']
EMAIL_RECIPMENTS = os.environ['EMAIL_RECIPMENTS']


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
    sat_pegaso_uuid = fields.Char(string="UUID")
    sat_pegaso_status = fields.Char(string="Status")
    sat_pegaso_ok = fields.Boolean("Timbrado")
    recurring_payment_days = fields.Integer(
        default = 7,
        string = "Dias de Pago",
        )
    #################################

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        self.sat_uso_id = self.partner_id.fiscal_address.sat_uso_id
        self.sat_metodo_pago = self.partner_id.fiscal_address.sat_metodo_pago
        self.sat_pagos_id = self.partner_id.fiscal_address.sat_pagos_id
        self.recurring_payment_days = self.recurring_payment_days

    @api.multi
    def action_invoice_open(self):
        # lots of duplicate calls to action_invoice_open, so we remove those already open
        to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
        if to_open_invoices.filtered(lambda inv: inv.state not in ['proforma2', 'draft']):
            raise UserError(_("Invoice must be in draft or Pro-forma state in order to validate it."))
        to_open_invoices.action_date_assign()
        to_open_invoices.action_move_create()
        return to_open_invoices.invoice_validate()

    #Take the data from teh invoice lines and return row/dict
    @api.one
    def action_cfdi_lines(self):
        rows =[]
        for line in self.invoice_line_ids:
            dict_rows = {
                "product_name" : line.product_id.name,
                "quantity" : line.quantity,
                "price_unit" : line.price_unit,
                "name" : line.name,
                "clave_sat" : line.product_id.clave_sat,
                "codigo_sat" : line.product_id.codigo_sat,
                "clave_unidad" : line.product_id.clave_unidad
            }
            rows.append(dict_rows) 
        return rows

    #Take the data from teh invoice lines and return row/dict
    @api.one
    def action_cfdi_lines_multi(self,parameter_data):
        rows =[]
        for line in parameter_data.invoice_line_ids:
           dict_rows = {
                "product_name" : line.product_id.name,
                "quantity" : line.quantity,
                "price_unit" : line.price_unit,
                "name" : line.name,
                "clave_sat" : line.product_id.clave_sat,
                "codigo_sat" : line.product_id.codigo_sat,
                "clave_unidad" : line.product_id.clave_unidad
           }
           rows.append(dict_rows) 
        return rows

    #Reads data from single invoices view and made the request for the cfdi
    @api.one
    def action_invoice_cfdi(self):
        #Prepare Folio and serie
        invoice_id = self.number.split("/")
        invoice_lines = self.action_cfdi_lines()
        
        
        #Prepare dict info for request info 
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
         'invoice_folio': invoice_id[1]+invoice_id[2],
         'invoice_products': invoice_lines,
         'invoice_products_line': self.invoice_line_ids,
         'invoice_date': self.action_cfdi_paremeters(),
         #'invoice_date': self.date_invoice.strftime(satLocalFormat),
         'amount_untaxed': "{:10.4f}".format(self.amount_untaxed),
         'amount_tax': self.amount_tax,
         'amount_total': self.amount_total,
         'sat_metodo_pago': self.sat_metodo_pago
         }
        _logger.info('send message to debug')
        _logger.info("self:{}".format(self))
        _logger.info('send message to info')
        if self.amount_tax != 0:
            CFDIRequest = self.CreateCFDIRequest(client_dict)
        else:
            CFDIRequest = self.CreateCFDIRequestNoTax(client_dict)
        CFDIRequest_2 = CFDIRequest.replace('<RequestCFD>','<RequestCFD version="3.3">')
        _logger.info("CFDIRequest: {}".format(CFDIRequest_2))
        contents = BASE_XML.format(CFDIRequest_2)
        # Send Data to Pegaso
        url = REQUEST_URL
        headers = {"Content-Type": "text/xml" , "SOAPAction": HEADER_SOAPACTION}
        response = requests.post(url, data=contents, headers=headers)
        result_cfdi=self.response_cfdi_data(response.content,'Transaccion',info = True)
        result_cfdi_TFD=self.response_cfdi_data(response.content,'TFD',info = True)
        self.write({'sat_pegaso_request': CFDIRequest_2})
        #Send data to log
        _logger.info(response.text)
        self.write({'sat_pegaso_response': response.text })
        self.write({'sat_pegaso_status': result_cfdi['estatus']})
        self.write({'sat_pegaso_uuid': result_cfdi_TFD['UUID']})

        return True

    #Reads data from invoices list view and made the request for the cfdi
    @api.multi
    def action_invoice_cfdi_multi(self):
        _logger.info("*********************** Call by action_invoice_cfdi_multi ***********************")
        for line in self:
            if not line.sat_pegaso_uuid and line.state =='open':
                #Prepare Folio and serie
                invoice_id = line.number.split("/")
                invoice_lines = self.action_cfdi_lines_multi(line)
                
                
                #Prepare dict info for request info 
                client_dict = {'customer_name': line.partner_id.name,
                 'date': line.date_invoice,
                 'customer_rfc': line.partner_id.rfc,
                 'customer_payment_id': line.sat_pagos_id.codigo_forma,
                 'customer_payment_name': line.sat_pagos_id.nombre_forma,
                 'customer_payment_use_id': line.sat_uso_id.codigo_uso,
                 'customer_payment_use_name': line.sat_uso_id.nombre_uso,
                 'customer_email': line.partner_id.email,
                 'invoice_id': line.number,
                 'invoice_series': invoice_id[0],
                 'invoice_folio': invoice_id[1]+invoice_id[2],
                 'invoice_products': invoice_lines,
                 'invoice_products_line': line.invoice_line_ids,
                 'invoice_date': self.action_cfdi_paremeters(),
                 #'invoice_date': self.date_invoice.strftime(satLocalFormat),
                 'amount_untaxed': "{:10.4f}".format(line.amount_untaxed),
                 'amount_tax': line.amount_tax,
                 'amount_total': line.amount_total,
                 'sat_metodo_pago': line.sat_metodo_pago
                 }

                if line.amount_tax != 0:
                    CFDIRequest = self.CreateCFDIRequest(client_dict)
                else:
                    CFDIRequest = self.CreateCFDIRequestNoTax(client_dict)

                if CFDIRequest.get('status_flag'):

                    CFDIRequest_2 = CFDIRequest.get('contents').replace('<RequestCFD>','<RequestCFD version="3.3">')

                    _logger.info("CFDIRequest: {}".format(CFDIRequest_2))
                    contents = BASE_XML.format(CFDIRequest_2)
                    line.write({'sat_pegaso_request': CFDIRequest_2})

                    # Send Data to Pegaso
                    url = REQUEST_URL
                    headers = {"Content-Type": "text/xml" , "SOAPAction": HEADER_SOAPACTION}
                    response = requests.post(url, data=contents, headers=headers)
                    line.write({'sat_pegaso_response': response.text })
                    # Process Response
                    result_cfdi=self.response_cfdi_data(response.content,'Transaccion',info = True)
                    result_cfdi_TFD=self.response_cfdi_data(response.content,'TFD',info = True)
                    # Write results
                
                    
                    line.write({'sat_pegaso_status': result_cfdi.get('estatus','N/A')})
                    line.write({'sat_pegaso_uuid': result_cfdi_TFD.get('UUID',None)})
                    line.write({'sat_pegaso_ok': True })
                    _logger.info("CFDIResponse uuid: {}".format(result_cfdi_TFD.get('UUID','')))
                else:
                    line.write({'sat_pegaso_request': CFDIRequest.get('contents')})
                    line.write({'sat_pegaso_response': "ERROR" })
                    line.write({'sat_pegaso_status': False})
                    #line.write({'sat_pegaso_uuid': None })
                    line.write({'sat_pegaso_ok': False })

            else:
                _logger.info("*********************** Do nothing in action_invoice_cfdi_multi ***********************")

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    # Returns the date to use on cdfi request format.
    @api.one
    def action_cfdi_paremeters(self):
        utcmoment_naive = datetime.utcnow()
        #utcmoment_naive = cfdi_date
        utcmoment = utcmoment_naive.replace(tzinfo=pytz.utc)
        satLocalFormat = "%Y-%m-%dT%H:%M:%S"
        satTimeZone = 'America/Mexico_City'
        localDatetime = utcmoment.astimezone(pytz.timezone(satTimeZone))
        satDateCFDI = localDatetime.strftime(satLocalFormat)

        return satDateCFDI

    #@api.one
    #Create CFDI request contents using RequestCFD_v33, RequestCFD_v33 was generated from the correspondent xsd file 
    # that defines rules fro the request.   
    def CreateCFDIRequest(self,cfdi_data):
        _logger.info("*********************** Call by CreateCFDIRequest ***********************")
        status_flag = True
        try:
            fecha= self.action_cfdi_paremeters()
            #Correct date and transaction id
            utcmoment_naive = datetime.utcnow()
            utcmoment = utcmoment_naive.replace(tzinfo=pytz.utc)
            satLocalFormat = "%Y-%m-%dT%H:%M:%S"
            satTimeZone = 'America/Mexico_City'
            localDatetime = utcmoment.astimezone(pytz.timezone(satTimeZone))
            satDateCFDI = localDatetime.strftime(satLocalFormat)

            #First create main document request
            requestCFD = api_cfdi.RequestCFD()
            requestCFD.set_version(version="3.3")
            #Second add comprobant to requestCFD nested element inside requestCFD
            #General Invoice Data
            #comprobanteType = api_cfdi.ComprobanteType(LugarExpedicion='15900' ,MetodoPago='PUE' ,TipoDeComprobante='I', Total="6000.05", SubTotal="6000.05" ,Moneda='MXN', FormaPago='03', Folio='833', Serie='VD' , Fecha="2020-06-12T10:42:02" )
            comprobanteType = api_cfdi.ComprobanteType(LugarExpedicion=EMISOR_LUGAR ,MetodoPago=cfdi_data['sat_metodo_pago'] ,TipoDeComprobante='I', Total=cfdi_data['amount_total'], SubTotal=cfdi_data['amount_untaxed'] ,Impuestos=cfdi_data['amount_tax'] ,Moneda='MXN', FormaPago=cfdi_data['customer_payment_id'].zfill(2), Folio=cfdi_data['invoice_folio'], Serie=cfdi_data['invoice_series'] , Fecha=satDateCFDI )
            #Emisor Data
            emisorType = api_cfdi.EmisorType(Rfc = EMISOR_RFC, Nombre= EMISOR_NOMBRE, RegimenFiscal= EMISOR_REGIMENFISCAL)
            #Receptor Data
            receptorType = api_cfdi.ReceptorType(Rfc = cfdi_data['customer_rfc'], Nombre= cfdi_data['customer_name'], UsoCFDI= cfdi_data['customer_payment_use_id'],emailReceptor=cfdi_data['customer_email'])
            #Invoice Line Data
            conceptosType = api_cfdi.ConceptosType()
            #Invoice Taxes
            #if cfdi_data['amount_tax'] != 0:
            trasladosType = api_cfdi.TrasladosType()
            impuestosType = api_cfdi.ImpuestosType()
            impuestosType2 = api_cfdi.ImpuestosType2(TotalImpuestosTrasladados=cfdi_data['amount_tax'])
    
            trasladoType6=api_cfdi.TrasladoType6(Impuesto="002", TipoFactor="Tasa", TasaOCuota="0.160000", Importe=cfdi_data['amount_tax'])
            #trasladoType6.set_Traslado(Impuesto="002", TipoFactor="Tasa", TasaOCuota="0.160000", Importe="8.00")
            trasladosType5 = api_cfdi.TrasladosType5()

            trasladosType5.add_Traslado(trasladoType6)
            impuestosType2.set_Traslados(trasladosType5)

            #Add al concepts on invoice lines
            for line in cfdi_data['invoice_products_line']:
                conceptoType1 = api_cfdi.ConceptoType(ClaveProdServ = line.product_id.clave_sat, Cantidad=line.quantity, ClaveUnidad = line.product_id.clave_unidad, Unidad='1', ValorUnitario=line.price_unit, Importe=line.price_unit ,Descripcion=line.name)
                #if cfdi_data['amount_tax'] != 0:
                trasladoType = api_cfdi.TrasladoType(Base=line.price_unit, Impuesto="002", TipoFactor="Tasa", TasaOCuota="0.160000" ,Importe=line.price_unit*0.16)
                #trasladosType = api_cfdi.TrasladosType()
                trasladosType.add_Traslado(trasladoType)
                impuestosType.set_Traslados(trasladosType)
                #conceptoType1.set_Impuestos(trasladosType)
                conceptoType1.set_Impuestos(impuestosType)
                conceptosType.add_Concepto(conceptoType1)
                #if cfdi_data['amount_tax'] != 0:     

            comprobanteType.set_Impuestos(impuestosType2)
            comprobanteType.set_Conceptos(conceptosType)
            comprobanteType.set_Emisor(emisorType)
            comprobanteType.set_Receptor(receptorType)
            #transactionType = api_cfdi.TransaccionType(id=cfdi_data['invoice_date'])
            transactionType = api_cfdi.TransaccionType(id=satDateCFDI+cfdi_data['invoice_series']+cfdi_data['invoice_folio'])
            #transactionType=satTransactionID
            tipoComprobante = api_cfdi.TipoComprobanteType(clave="Factura", nombre="Factura")
            sucursal = api_cfdi.SucursalType(nombre="MATRIZ")
            receptor= api_cfdi.ReceptorType7(emailReceptor=cfdi_data['customer_email']+';'+EMAIL_RECIPMENTS)
            #impuestos = api_cfdi.ImpuestosType2(TotalImpuestosTrasladados=cfdi_data['amount_tax']
            #comprobanteType.set_Impuestos(impuestos)
            requestCFD.set_Comprobante(comprobanteType)
            requestCFD.set_Transaccion(transactionType)
            requestCFD.set_TipoComprobante(tipoComprobante)
            requestCFD.set_Sucursal(sucursal)
            requestCFD.set_Receptor(receptor)

            salida = open(TEMPORAL_OUT_XML,"w+") 
            requestCFD.export(salida,0)
            salida.close()

            # Save Request to file
            f = open(TEMPORAL_OUT_XML,"r")
            if f.mode == 'r':
                contents =f.read()
            f.close()

            contents_full = BASE_XML.format(contents)
            contents_full_2 = contents_full.replace('<RequestCFD>','<RequestCFD version="3.3">')
            file = open(TEMPORAL_OUT_XML_OK,"w")
            file.write(contents_full_2)
            file.close()

        except Exception as e:
            _logger.info("*********************** Error on Call by CreateCFDIRequest ***********************")
            _logger.info(e)
            _logger.info("*********************** ********************************** ***********************")
            _logger.info(traceback.format_exc())
            _logger.info("*********************** ********************************** ***********************")
            _logger.info(cfdi_data)
            _logger.info("*********************** ********************************** ***********************")
            contents = "CreateCFDIRequest problem: {} |**************| cfdi_data: {}".format(str(e),str(cfdi_data))

            #contents += "**************"
            #contents += "cfdi_data: {}".format(str(cfdi_data))
            status_flag = False

        return {'contents' : contents, 'status_flag': status_flag}


    def CreateCFDIRequestNoTax(self,cfdi_data):
        _logger.info("*********************** Call by CreateCFDIRequestNoTax ***********************")
        status_flag = True
        try:
            fecha= self.action_cfdi_paremeters()
            #Correct date and transaction id
            utcmoment_naive = datetime.utcnow()
            utcmoment = utcmoment_naive.replace(tzinfo=pytz.utc)
            satLocalFormat = "%Y-%m-%dT%H:%M:%S"
            satTimeZone = 'America/Mexico_City'
            localDatetime = utcmoment.astimezone(pytz.timezone(satTimeZone))
            satDateCFDI = localDatetime.strftime(satLocalFormat)

            #First create main document request
            requestCFD = api_cfdi.RequestCFD()
            requestCFD.set_version(version="3.3")
            #Second add comprobant to requestCFD nested element inside requestCFD
            #General Invoice Data
            #comprobanteType = api_cfdi.ComprobanteType(LugarExpedicion='15900' ,MetodoPago='PUE' ,TipoDeComprobante='I', Total="6000.05", SubTotal="6000.05" ,Moneda='MXN', FormaPago='03', Folio='833', Serie='VD' , Fecha="2020-06-12T10:42:02" )
            comprobanteType = api_cfdi.ComprobanteType(LugarExpedicion=EMISOR_LUGAR ,MetodoPago=cfdi_data['sat_metodo_pago'] ,TipoDeComprobante='I', Total=cfdi_data['amount_total'], SubTotal=cfdi_data['amount_untaxed'] ,Moneda='MXN', FormaPago=cfdi_data['customer_payment_id'].zfill(2), Folio=cfdi_data['invoice_folio'], Serie=cfdi_data['invoice_series'] , Fecha=satDateCFDI )
            #Emisor Data
            emisorType = api_cfdi.EmisorType(Rfc = EMISOR_RFC, Nombre= EMISOR_NOMBRE, RegimenFiscal= EMISOR_REGIMENFISCAL)
            #Receptor Data
            receptorType = api_cfdi.ReceptorType(Rfc = cfdi_data['customer_rfc'], Nombre= cfdi_data['customer_name'], UsoCFDI= cfdi_data['customer_payment_use_id'],emailReceptor=cfdi_data['customer_email'])
            #Invoice Line Data
            conceptosType = api_cfdi.ConceptosType()
            #Invoice Taxes
            #if cfdi_data['amount_tax'] != 0:
            #trasladosType = api_cfdi.TrasladosType()
            #impuestosType = api_cfdi.ImpuestosType()
            #impuestosType2 = api_cfdi.ImpuestosType2(TotalImpuestosTrasladados=cfdi_data['amount_tax'])
    
            #trasladoType6=api_cfdi.TrasladoType6(Impuesto="002", TipoFactor="Tasa", TasaOCuota="0.160000", Importe=cfdi_data['amount_tax'])
            #trasladoType6.set_Traslado(Impuesto="002", TipoFactor="Tasa", TasaOCuota="0.160000", Importe="8.00")
            #trasladosType5 = api_cfdi.TrasladosType5()

            #trasladosType5.add_Traslado(trasladoType6)
            #impuestosType2.set_Traslados(trasladosType5)

            #Add al concepts on invoice lines
            for line in cfdi_data['invoice_products_line']:
                conceptoType1 = api_cfdi.ConceptoType(ClaveProdServ = line.product_id.clave_sat, Cantidad=line.quantity, ClaveUnidad = line.product_id.clave_unidad, Unidad='1', ValorUnitario=line.price_unit, Importe=line.price_unit ,Descripcion=line.name)
                #if cfdi_data['amount_tax'] != 0:
                #trasladoType = api_cfdi.TrasladoType(Base=line.price_unit, Impuesto="002", TipoFactor="Tasa", TasaOCuota="0.160000" ,Importe=line.price_unit*0.16)
                #trasladosType = api_cfdi.TrasladosType()
                #trasladosType.add_Traslado(trasladoType)
                #impuestosType.set_Traslados(trasladosType)
                #conceptoType1.set_Impuestos(trasladosType)
                #conceptoType1.set_Impuestos(impuestosType)
                conceptosType.add_Concepto(conceptoType1)
                #if cfdi_data['amount_tax'] != 0:     
                
            #comprobanteType.set_Impuestos(impuestosType2)
            comprobanteType.set_Conceptos(conceptosType)
            comprobanteType.set_Emisor(emisorType)
            comprobanteType.set_Receptor(receptorType)
            #transactionType = api_cfdi.TransaccionType(id=cfdi_data['invoice_date'])
            transactionType = api_cfdi.TransaccionType(id=satDateCFDI+cfdi_data['invoice_series']+cfdi_data['invoice_folio'])
            #transactionType=satTransactionID
            tipoComprobante = api_cfdi.TipoComprobanteType(clave="Factura", nombre="Factura")
            sucursal = api_cfdi.SucursalType(nombre="MATRIZ")
            receptor= api_cfdi.ReceptorType7(emailReceptor=cfdi_data['customer_email']+';'+EMAIL_RECIPMENTS)
            #impuestos = api_cfdi.ImpuestosType2(TotalImpuestosTrasladados=cfdi_data['amount_tax']
            #comprobanteType.set_Impuestos(impuestos)
            requestCFD.set_Comprobante(comprobanteType)
            requestCFD.set_Transaccion(transactionType)
            requestCFD.set_TipoComprobante(tipoComprobante)
            requestCFD.set_Sucursal(sucursal)
            requestCFD.set_Receptor(receptor)

            salida = open(TEMPORAL_OUT_XML,"w+") 
            requestCFD.export(salida,0)
            salida.close()

            # Save Request to file
            f = open(TEMPORAL_OUT_XML,"r")
            if f.mode == 'r':
                contents =f.read()
            f.close()

            contents_full = BASE_XML.format(contents)
            contents_full_2 = contents_full.replace('<RequestCFD>','<RequestCFD version="3.3">')
            file = open(TEMPORAL_OUT_XML_OK,"w")
            file.write(contents_full_2)
            file.close()

        except Exception as e:
            _logger.info("*********************** Error on Call by CreateCFDIRequestNoTax ***********************")
            _logger.info(e)
            _logger.info("*********************** ********************************** ***********************")
            _logger.info(traceback.format_exc())
            _logger.info("*********************** ********************************** ***********************")
            _logger.info(cfdi_data)
            _logger.info("*********************** ********************************** ***********************")
            contents = "CreateCFDIRequest problem: {} |**************| cfdi_data: {}".format(str(e),str(cfdi_data))

            #contents += "**************"
            #contents += "cfdi_data: {}".format(str(cfdi_data))
            status_flag = False

        return {'contents' : contents, 'status_flag': status_flag}


    #Takes the response from pegaso CDFI XML Element and return the requested attrib elements
    def response_cfdi_data(self,contents_xml,data_selector,info = True):
        root = etree.XML(contents_xml)
        if info:
            for idt,element in enumerate(root.iter()):
                _logger.info("%s .- %s || %s" % (idt, element.tag, element.text))

        option = {
            'Envelope': '{http://schemas.xmlsoap.org/soap/envelope/}Envelope',
            'Header': '{http://schemas.xmlsoap.org/soap/envelope/}Header',
            'Body': '{http://schemas.xmlsoap.org/soap/envelope/}Body',
            'emitirCFDResponse': '{http://namespace.pegasotecnologia.com/SCFD}emitirCFDResponse',
            'emitirCFDResult': 'http://namespace.pegasotecnologia.com/SCFD}emitirCFDResult',
            'ResponseAdmon': '{http://www.pegasotecnologia.com/}ResponseAdmon',
            'Transaccion': '{http://www.pegasotecnologia.com/}Transaccion',
            'CFD': '{http://www.pegasotecnologia.com/}CFD',
            'TFD': '{http://www.pegasotecnologia.com/}TFD',
            'Error':'{http://www.pegasotecnologia.com/}Error',
            'Comprobante': 'Comprobante'
        }
        loop_atrib = {}
        for idx, item in enumerate(root.iter(option[data_selector])):
            loop_atrib=item.attrib
            _logger.info("loop_atrib: {}".format(loop_atrib))
        return loop_atrib   