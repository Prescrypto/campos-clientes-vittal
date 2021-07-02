# -*- coding: utf-8 -*-
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

my_cfdi_data = {'sat_metodo_pago': 'PUE', 
    'customer_email': 'juanmanuelriverom@gmail.com', 
    'amount_untaxed': ' 2000.0000', 
    'invoice_folio': '20200025', 
    'customer_payment_use_name': 'Gastos en general', 
    'invoice_id': 'INV/2020/0025', 
    'invoice_date': ['2020-07-31T19:52:44'], 
    'customer_payment_name': 'Transferencia electr\xf3nica de fondos', 
    'amount_tax': 3.21, 
    'invoice_products': [[{'name': u'[Areaprotegida1] Area Protegida', 'price_unit': 2000.0, 'clave_sat': u'85121800', 'clave_unidad': u'E48', 'product_name': u'Area Protegida', 'codigo_sat': u'85121800', 'quantity': 1.0}]], 
    #'invoice_products_line': account.invoice.line(26,), 
    'invoice_products_line': [[{'name': u'[Areaprotegida1] Area Protegida', 'price_unit': 2000.0, 'clave_sat': u'85121800', 'clave_unidad': u'E48', 'product_name': u'Area Protegida', 'codigo_sat': u'85121800', 'quantity': 1.0}]], 
    'customer_payment_use_id': u'G03',
    'customer_rfc': u'ICB190208AN4', 
    'date': '2020-07-30', 
    'amount_total': 2003.21, 
    'invoice_series': u'INV', 
    'customer_payment_id': u'3', 
    'customer_name': u'ilco empresa'
}

def CreateCFDIRequest(cfdi_data):
    #_logger.debug("*********************** Call by CreateCFDIRequest ***********************")
    line_element = []
    line_dict= {'name': u'[Areaprotegida1] Area Protegida', 'price_unit': 2000.0, 'clave_sat': u'85121800', 'clave_unidad': u'E48', 'product_name': u'Area Protegida', 'codigo_sat': u'85121800', 'quantity': 1.0}
    line_element.append(line_dict)

    status_flag = True
#try:
    #fecha= self.action_cfdi_paremeters()
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
    trasladosType = api_cfdi.TrasladosType()
    impuestosType = api_cfdi.ImpuestosType()
    impuestosType2 = api_cfdi.ImpuestosType2(TotalImpuestosTrasladados="3.21")
    
    trasladoType6=api_cfdi.TrasladoType6(Impuesto="002", TipoFactor="Tasa", TasaOCuota="0.160000", Importe="3.21")
    #trasladoType6.set_Traslado(Impuesto="002", TipoFactor="Tasa", TasaOCuota="0.160000", Importe="8.00")
    trasladosType5 = api_cfdi.TrasladosType5()

    trasladosType5.add_Traslado(trasladoType6)
    impuestosType2.set_Traslados(trasladosType5)
    #impuestosType2.a

    #Add al concepts on invoice lines
    #for line in cfdi_data['invoice_products_line']:
    for line in line_element:
        #conceptoType1 = api_cfdi.ConceptoType(ClaveProdServ = line.product_id.clave_sat, Cantidad=line.quantity, ClaveUnidad = line.product_id.clave_unidad, Unidad='1', ValorUnitario=line.price_unit, Importe=line.price_unit ,Descripcion=line.product_id.name)
        conceptoType1 = api_cfdi.ConceptoType(ClaveProdServ = line['clave_sat'], Cantidad=line['quantity'], ClaveUnidad = line['clave_unidad'], Unidad='1', ValorUnitario=line['price_unit'], Importe=line['price_unit'] ,Descripcion=line['name'])
        #trsaladoType = api_cfdiTrasladoType
        trasladoType = api_cfdi.TrasladoType(Base="2000.00", Impuesto="002", TipoFactor="Tasa", TasaOCuota="0.160000" ,Importe="3.21")
        #trasladosType = api_cfdi.TrasladosType()
        trasladosType.add_Traslado(trasladoType)
        impuestosType.set_Traslados(trasladosType)
        #trasladosType.set_Traslados(trasladoType)
        #conceptoType1.set_Impuestos(trasladosType)
        conceptoType1.set_Impuestos(impuestosType)
        #conceptoType1.set_tras
        #print("*********** Traslados:{}".format(**trasladosType))

        #impuestosType = api_cfdi.ImpuestosType()
        #impuestosType.set_Traslado(trasladosType)
        #impuestosType.set_Traslado(base=""  Impuesto="002", TipoFactor="Tasa", TasaOCuota="0.160000" ,Importe="3.21")
        #conceptosType.set_Impuestos(impuestosType)
        conceptosType.add_Concepto(conceptoType1)
        #conceptosType.add_Impuestos(impuestosType)
        #conceptosType.add_Traslados(TrasladosType)
    #impuestosType.set_Traslados(trasladosType)
    #conceptosType.set_Impuestos(impuestosType)

    comprobanteType.set_Impuestos(impuestosType2)
    comprobanteType.set_Conceptos(conceptosType)
    comprobanteType.set_Emisor(emisorType)
    comprobanteType.set_Receptor(receptorType)
    transactionType = api_cfdi.TransaccionType(id=cfdi_data['invoice_date'])
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
#except Exception as e:
    # _logger.debug("*********************** Error on Call by CreateCFDIRequest ***********************")
    # _logger.debug(e)
    # _logger.debug("*********************** ********************************** ***********************")
    # _logger.debug(traceback.format_exc())
    # _logger.debug("*********************** ********************************** ***********************")
    # _logger.debug(cfdi_data)
    # _logger.debug("*********************** ********************************** ***********************")


    print("*********************** Error on Call by CreateCFDIRequest ***********************")
    #print(e)
    print("*********************** ********************************** ***********************")
    #print(traceback.format_exc())
    print("*********************** ********************************** ***********************")
    print(cfdi_data)
    print("*********************** ********************************** ***********************")

    contents = "CreateCFDIRequest problem: {} |**************| cfdi_data: {}".format(str(""),str(cfdi_data))

    #contents += "**************"
    #contents += "cfdi_data: {}".format(str(cfdi_data))
    status_flag = False

    return {'contents' : contents, 'status_flag': status_flag}

my_result = CreateCFDIRequest(my_cfdi_data)
print("Result: {}".format(my_result))