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
#import xmltodict, json

_logger = logging.getLogger(__name__)

#
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

# EMISOR_RFC = 'TMO1104114Y9'
# EMISOR_NOMBRE = 'TIEMPOREAL_TMO1104114Y9_ws'
# EMISOR_REGIMENFISCAL = '601'
# EMISOR_LUGAR = '15900'
# TIMEOUT_TOLERANCE = 25
# HEADER_SOAPACTION="http://namespace.pegasotecnologia.com/SCFD/IEmisionBaseExternalService/emitirCFD"
# REQUEST_URL = "https://qa.pegasotecnologia.mx/ServAdmEmisionGatewayQA/ServiceGateway.svc/Soap11Text"
#TEMPORAL_OUT_XML = 'prescrypto/campos_clientes_vittal/campos_clientes_vittal/models/request_2020_06_30.xml'
#TEMPORAL_OUT_XML_OK = 'prescrypto/campos_clientes_vittal/campos_clientes_vittal/models/full_cfdi_request.xml'

#TEMPORAL_OUT_XML = 'request_2020_06_30.xml'
#TEMPORAL_OUT_XML_OK = 'full_cfdi_request.xml'

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
    def action_cfdi_lines(self):
        rows =[]
        for line in self.invoice_line_ids:
           dict_rows = {}
           dict_rows["product_name"] = line.product_id.name
           dict_rows["quantity"]= line.quantity
           dict_rows["price_unit"]= line.price_unit
           dict_rows["name"]= line.name
           dict_rows["clave_sat"]= line.product_id.clave_sat
           dict_rows["codigo_sat"]= line.product_id.codigo_sat
           dict_rows["clave_unidad"]=line.product_id.clave_unidad

           # {'product_name': line.product_id.name,
           #              'quantity': line.quantity,
           #              'price_unit': line.price_unit,
           #              'name':line.name,
           #              'clave_sat':line.product_id.clave_sat,
           #              'codigo_sat':line.product_id.codigo_sat,
           #              'clave_unidad':line.product_id.clave_unidad
           # }
           rows.append(dict_rows) 
        return rows

    @api.one
    def action_invoice_cfdi(self):
        invoice_id = self.number.split("/")
        invoice_lines = self.action_cfdi_lines()
        
        

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
        _logger.debug('send message to debug')
        _logger.debug("self:{}".format(self))
        _logger.info('send message to info')
        #self.CreateCFDIRequest(client_dict)
        CFDIRequest = self.CreateCFDIRequest(client_dict)
        CFDIRequest_2 = CFDIRequest.replace('<RequestCFD>','<RequestCFD version="3.3">')
        print("CFDIRequest: {}".format(CFDIRequest_2))
        contents = BASE_XML.format(CFDIRequest_2)
        # Send Data to Pegaso
        url = REQUEST_URL
        headers = {"Content-Type": "text/xml" , "SOAPAction": HEADER_SOAPACTION}
        response = requests.post(url, data=contents, headers=headers)
        #print("response: {}".format(response.text))
        #result = self.SendCFDIREquest(TEMPORAL_OUT_XML_OK)
        result_cfdi=self.response_cfdi_data(response.content,'Transaccion',info = True)
        result_cfdi_TFD=self.response_cfdi_data(response.content,'TFD',info = True)
        #Write results
        #self.write({'sat_pegaso_request': str(client_dict) + "***************\n" +  CFDIRequest_2})
        self.write({'sat_pegaso_request': CFDIRequest_2})
        #self.write({'sat_pegaso_response': response.content })
        _logger.debug(response.text)
        self.write({'sat_pegaso_response': response.text })
        self.write({'sat_pegaso_status': result_cfdi['estatus']})
        self.write({'sat_pegaso_uuid': result_cfdi_TFD['UUID']})

        return True
        
    @api.one
    def action_cfdi_paremeters(self):
        utcmoment_naive = datetime.utcnow()
        #utcmoment_naive = cfdi_date
        utcmoment = utcmoment_naive.replace(tzinfo=pytz.utc)
        satLocalFormat = "%Y-%m-%dT%H:%M:%S"
        satTimeZone = 'America/Mexico_City'
        localDatetime = utcmoment.astimezone(pytz.timezone(satTimeZone))
        satDateCFDI = localDatetime.strftime(satLocalFormat)
        #print("Fecha: {}".format(satDateCFDI))
        #fecha= "{}".format(satDateCFDI)
        #fecha_2 = fecha.replace("[","")
        #fecha_3 = fecha_2.replace("]","")
        return satDateCFDI

    #@api.one
    def CreateCFDIRequest(self,cfdi_data):
        fecha= self.action_cfdi_paremeters()
        print("fecha: {}".format(fecha))
        my_subtotal="2000"
        #Correct date and transaction id
        utcmoment_naive = datetime.utcnow()
        utcmoment = utcmoment_naive.replace(tzinfo=pytz.utc)
        satLocalFormat = "%Y-%m-%dT%H:%M:%S"
        satTimeZone = 'America/Mexico_City'
        localDatetime = utcmoment.astimezone(pytz.timezone(satTimeZone))
        satDateCFDI = localDatetime.strftime(satLocalFormat)
        #satLocalFormatTransactionID = "%Y%m%d%H%M%S"
        #satTransactionID=localDatetime.strftime(satLocalFormatTransactionID)
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
        # for lines in cfdi_data['invoice_products']:
        #     #conceptoType1 = api_cfdi.ConceptoType(ClaveProdServ = '43232605', Cantidad='1', ClaveUnidad = '48', Unidad='1', ValorUnitario="6000.05", Importe="6000.05" ,Descripcion='Servicio Medico')
        #     conceptoType1 = api_cfdi.ConceptoType(ClaveProdServ = lines['clave_sat'], Cantidad=lines['quantity'], ClaveUnidad = lines['clave_unidad'], Unidad='1', ValorUnitario=line['price_unit'], Importe=line['price_unit'] ,Descripcion=line['name'])
        #     #conceptoType2 = api.ConceptoType(ClaveProdServ = '43232605', Cantidad='2', ClaveUnidad = '48', Unidad='1', ValorUnitario= '111.00', Importe='22.00' ,Descripcion='Servicio Medico 22')
        #     conceptosType.add_Concepto(conceptoType1)
        #conceptosType.add_Concepto(conceptoType2)
        for line in cfdi_data['invoice_products_line']:
            conceptoType1 = api_cfdi.ConceptoType(ClaveProdServ = line.product_id.clave_sat, Cantidad=line.quantity, ClaveUnidad = line.product_id.clave_unidad, Unidad='1', ValorUnitario=line.price_unit, Importe=line.price_unit ,Descripcion=line.product_id.name)
            conceptosType.add_Concepto(conceptoType1)


        comprobanteType.set_Conceptos(conceptosType)
        comprobanteType.set_Emisor(emisorType)
        comprobanteType.set_Receptor(receptorType)
        transactionType = api_cfdi.TransaccionType(id=cfdi_data['invoice_date'])
        #transactionType=satTransactionID
        tipoComprobante = api_cfdi.TipoComprobanteType(clave="Factura", nombre="Factura")
        sucursal = api_cfdi.SucursalType(nombre="MATRIZ")
        receptor= api_cfdi.ReceptorType7(emailReceptor=cfdi_data['customer_email']+';'+EMAIL_RECIPMENTS)
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
        return contents

    # def SendCFDIREquest(self,file_data):
    #     f = open(file_data,"r")
    #     if f.mode == 'r':
    #         contents =f.read()
    #     f.close()
    #     # Payload
    #     url = REQUEST_URL
    #     #payload = {'username': 'TIEMPOREAL_TMO1104114Y9_ws ', 'password': ''}
    #     #headers = {"Content-Type": "text/html"}

    #     headers = {"Content-Type": "text/xml" , "SOAPAction": HEADER_SOAPACTION}
    #     #response = requests.post(url, data=contents, headers=headers)
    #     response = requests.post(url, data=contents, headers=headers)
    #     #response = requests.put(url, data=contents, headers=headers)
    #     #response = 
    #     print("********************** DATA SEND **********************")
    #     print("{}".format(contents))
    #     print("*******************************************************")
    #     print("********************** ANSWER *************************")
    #     print("{}".format(response))
    #     print("************************RESPONSE CONTENT*******************************")
    #     print(response.content)
    #     print("************************RESPONSE RAW 100 *******************************")
    #     print(response.raw.read(100))
    #     print("*********************** RESPONSE HEADERS********************************")
    #     print(response.headers)
    #     print("*********************** RESPONSE TEXT ********************************")
    #     print(response.text)
    #     print("*********************** RESPONSE DICT *************************")
    #     o = xmltodict.parse(response.content)
    #     print(json.dumps(o))
    #     return response 

    def response_cfdi_data(self,contents_xml,data_selector,info = True):
        root = etree.XML(contents_xml)
        if info:
            for idt,element in enumerate(root.iter()):
                print("%s .- %s || %s" % (idt, element.tag, element.text))

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
        for idx, item in enumerate(root.iter(option[data_selector])):
            #print(idx)
            #print(movie.attrib)
            loop_atrib=item.attrib
            print("{}".format(loop_atrib))
        return loop_atrib   