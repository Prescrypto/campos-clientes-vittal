# encoding=utf8
#import xmlschema
import sys
from pprint import pprint
import datetime
import RequestCFD_v33 as api
import requests

from zeep import Client
from zeep import xsd

import xmltodict, json


EMISOR_RFC = 'TMO1104114Y9'
EMISOR_NOMBRE = 'TIEMPOREAL_TMO1104114Y9_ws'
EMISOR_REGIMENFISCAL = '612'
EMISOR_LUGAR = '15900'
TIMEOUT_TOLERANCE = 25

HEADER_SOAPACTION="http://namespace.pegasotecnologia.com/SCFD/IEmisionBaseExternalService/emitirCFD"

#REQUEST_URL = 'https://qa.pegasotecnologia.mx/ServAdmEmisionGatewayQA/ServiceGateway.svc/Soap11Text/'
#REQUEST_URL = 'https://qa.pegasotecnologia.mx/ServAdmEmisionGatewayQA/ServiceGateway.svc/Soap11Text'
#REQUEST_URL = 'https://qa.pegasotecnologia.com/SCFD/IEmisionBaseExternalService/emitirCFD'
#REQUEST_URL = 'https://qa.pegasotecnologia.mx/ServAdmEmisionGatewayQA/ServiceGateway.svc/'
REQUEST_URL = "https://qa.pegasotecnologia.mx/ServAdmEmisionGatewayQA/ServiceGateway.svc/Soap11Text"


#TEMPORAL_OUT_XML = 'Temp_Out_Request.xml'
#TEMPORAL_OUT_XML = 'request_2020_06.xml'
#TEMPORAL_OUT_XML = 'response_2020_07_01.xml'
TEMPORAL_OUT_XML = 'full_cfdi_request.xml'

INPUT_XSD_FILE = 'RequestCFD_v33_unix.xsd'

def CreateCFDIRequest(cfdi_data):
  #First create main document request
  requestCFD = api.RequestCFD()

  #Second add comprobant to requestCFD nested element inside requestCFD
  comprobanteType = api.ComprobanteType(LugarExpedicion='15900' ,MetodoPago='PUE' ,TipoDeComprobante='I', Total="6000.01", SubTotal="6000.10" ,Moneda='MXN', FormaPago='03', Folio='833', Serie='VD' , Fecha="2020-06-12T10:42:02" )

  emisorType = api.EmisorType(Rfc = EMISOR_RFC, Nombre= EMISOR_NOMBRE, RegimenFiscal= EMISOR_REGIMENFISCAL)
  receptorType = api.ReceptorType(Rfc = 'RIMJ7108165N0', Nombre= 'RIVERO MERCADO JUAN MANUEL', UsoCFDI= 'P01',emailReceptor='juanmanuelriverom@gmail.com')

  conceptoType1 = api.ConceptoType(ClaveProdServ = '43232605', Cantidad='1', ClaveUnidad = '48', Unidad='1', ValorUnitario="6000.00", Importe="6000.00" ,Descripcion='Servicio Medico')
  #conceptoType2 = api.ConceptoType(ClaveProdServ = '43232605', Cantidad='2', ClaveUnidad = '48', Unidad='1', ValorUnitario= '111.00', Importe='22.00' ,Descripcion='Servicio Medico 22')

  conceptosType = api.ConceptosType()

  conceptosType.add_Concepto(conceptoType1)
  #conceptosType.add_Concepto(conceptoType2)

  comprobanteType.set_Conceptos(conceptosType)
  comprobanteType.set_Emisor(emisorType)
  comprobanteType.set_Receptor(receptorType)
  transactionType = api.TransaccionType(id="20180420132024")
  tipoComprobante = api.TipoComprobanteType(clave="Factura", nombre="Factura")
  sucursal = api.SucursalType(nombre="Matriz")
  receptor= api.ReceptorType7(emailReceptor="juanmanuelriverom@gmail.com")

  #set_anytypeobjs_
  #complementoType = api.ComplementoType()
  #complementoType.set_ComplementoType(Pagos='01')

  #comprobanteType.add_Complemento(complementoType)

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
  print("{}".format(contents))
  return(requestCFD)


def SendCFDIREquest(file_data):
  f = open(file_data,"r")
  if f.mode == 'r':
    contents =f.read()
  f.close()
  # Payload
  url = REQUEST_URL
  #payload = {'username': 'TIEMPOREAL_TMO1104114Y9_ws ', 'password': ''}
  #headers = {"Content-Type": "text/html"}

  headers = {"Content-Type": "text/xml" , "SOAPAction": HEADER_SOAPACTION}
  #response = requests.post(url, data=contents, headers=headers)
  response = requests.post(url, data=contents, headers=headers)
  #response = requests.put(url, data=contents, headers=headers)
  #response = 
  print("********************** DATA SEND **********************")
  print("{}".format(contents))
  print("*******************************************************")
  print("********************** ANSWER *************************")
  print("{}".format(response))
  print("************************RESPONSE CONTENT*******************************")
  print(response.content)
  print("************************RESPONSE RAW 100 *******************************")
  print(response.raw.read(100))
  print("*********************** RESPONSE HEADERS********************************")
  print(response.headers)
  print("*********************** RESPONSE TEXT ********************************")
  print(response.text)
  print("*********************** RESPONSE DICT *************************")
  o = xmltodict.parse(response.content)
  print(json.dumps(o))
  return response

#def SendCFDI_Soap()

def ValidateCFDI(file_xsd,file_xml):
  #First Open xsd file
  schema_file = open(file_xsd, encoding="utf-8")
  schema = xmlschema.XMLSchema(schema_file)
  print('********************** TO_DICT **********************')
  pprint(schema.to_dict(file_xml))
  print("********************** IS_VALID ****************** ")
  pprint(schema.is_valid(file_xml))
  print("********************** VALIDATE ****************** ")
  schema.validate(file_xml)



#requestCFD.export(salida ,0)
#requestCFD.export(sys.stdout,0)
# Generar xml de request
#
#requestCFD.export(salida,0)
#salida.close()

#all_out= str(requestCFD)

#print("{}".format(salida))
#print("******************* CONTENTS **********************")
#f = open("guru99.xml", "r")
#f = open("cfdv33-base.xml","r",encoding="utf-8")
#f = open("Request_complementopago.xml", "r")
#if f.mode == 'r':
#  contents =f.read()
#	print("{}".format(contents))
#f.close()
# validate
#schema_file = open('RequestCFD_v33_unix.xsd', encoding="utf-8")
#schema = xmlschema.XMLSchema(schema_file)
#print('********************** TO_DICT **********************')
#pprint(schema.to_dict('guru99.xml'))

#print("********************** IS_VALID ****************** ")
#schema.is_valid('guru99.xml')
#print("********************** VALIDATE ****************** ")
#schema.validate('guru99.xml')
#schema.validate('Request_complementopago.xml')

#CreateCFDIRequest('bla',)
#ValidateCFDI(INPUT_XSD_FILE,TEMPORAL_OUT_XML)


#ValidateCFDI(INPUT_XSD_FILE,'ICB190208AN461d41d62-729b-43d6-9648-ab6b017902b1.xml')
#ValidateCFDI(INPUT_XSD_FILE,'Request_complementopago.txt')

#SendCFDIREquest('Request_complementopago.txt')
#SendCFDIREquest(TEMPORAL_OUT_XML)
#SendCFDIREquest('EjemploVidaUno.xml')


#TEMPORAL_OUT_XML = 'request_2020_06_29.xml'
CreateCFDIRequest(TEMPORAL_OUT_XML)
#SendCFDIREquest(TEMPORAL_OUT_XML)


