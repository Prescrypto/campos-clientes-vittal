#import datetime
from datetime import datetime
import pytz

from lxml import etree

import xml.etree.ElementTree as ET
# current_date_time = datetime.datetime.today()
# jstTimeDelta        = datetime.timedelta(hours=9)
# jstTZObject         = datetime.timezone(jstTimeDelta, name="JST")
# current_date_time_utc = current_date_time.astimezone(jstTZObject)
# dt_string = current_date_time.strftime('%Y-%m-%dT%I:%M:%S')
# print("Date/Time in dd/mm/yy Hour:Min Second AM/PM:", dt_string)

utcmoment_naive = datetime.utcnow()
utcmoment = utcmoment_naive.replace(tzinfo=pytz.utc)

# localFormat = "%Y-%m-%d %H:%M:%S"
# timezones = ['America/Mexico_City','America/Los_Angeles', 'Europe/Madrid', 'America/Puerto_Rico']

# for tz in timezones:
#     localDatetime = utcmoment.astimezone(pytz.timezone(tz))
#     print(localDatetime.strftime(localFormat))


satLocalFormat = "%Y-%m-%dT%H:%M:%S"
satTimeZone = 'America/Mexico_City'
localDatetime = utcmoment.astimezone(pytz.timezone(satTimeZone))
satDateCFDI = localDatetime.strftime(satLocalFormat)
print(satDateCFDI)


#file_data = "response_2020_06_26.xml"
#file_data = "bad_response_example.xml"
file_data = "full_cfdi_request.xml"

f = open(file_data,"r")
if f.mode == 'r':
	contents_xml =f.read()
f.close()

#root = etree.fromstring(contents_xml)
#print(root.tag)

#print("******************* 00 *******************")

#root = etree.XML(contents_xml)
#print(root.header)


# print(etree.tostring(root, pretty_print=True))

#print("******************* 01 *******************")

# for child in root:
# 	print(child.tag)


# print(root[1].get("emitirCFDResponse"))

#print("******************* 02 *******************")

# for name, value in sorted(root.items()):
#	print('%s = %r' % (name, value))

#print("******************* 03 *******************")
# print(root[1].keys())



# for idt,element in enumerate(root.iter()):
# 	print("%s .- %s || %s" % (idt, element.tag, element.text))
	# print('**************** item begin {} *****************'.format(idt))
	# for idx, item in enumerate(element.iter()):
	# 	print('**************** items begin {} *****************'.format(idx))
	# 	print("%s .- %s |-| %s" % (idx, item.tag, item.text))
	# 	print('**************** items end {} *****************'.format(idx))
	# print('**************** item end {} *****************'.format(idt))


#print("******************* 04 *******************")
# print("**************************************")
# #print(root.iterfind(".//Transaccion").tag)

# print("**************************************")
# tree = etree.ElementTree(root)
# a = root[1]
# print(tree.getelementpath(a[0]))


#root = ET.fromstring(contents_xml)
# print("tag: {}".format(root.tag))
# print("attrib: {}".format(root.attrib))
# #topic=root.find(".//*[@TFD='UUID']").text
# topic=root.find(".//*[@UUID]").text
# print(topic)

# print("******************* 05 *******************")

# # for child in root:
# # 	print child.tag, child.attrib

# print("******************* 06 *******************")
# for neighbor in root.iter('CFD'):
# 	print neighbor.attrib
# print("******************* 07 *******************")

# for country in root.findall('./Body/emitirCFDResponse/emitirCFDResult/ResponseAdmon/Transaccion'):
# 	rank = country.find('UUID').text
# 	name = country.get('FechaTimbrado')
# 	print name, rank

# print("******************* 08 *******************")

# for country in root.findall('{http://namespace.pegasotecnologia.com/SCFD}emitirCFDResult'):
# 	rank = country.find('{http://www.pegasotecnologia.com/}Transaccion').text
# 	#name = country.get('FechaTimbrado')
# 	#print name, rank
# 	print rank

# print("******************* 09 *******************")
#tree = ET.fromstring(contents_xml)
# tree = ET.parse('file_data')
# root = tree.getroot()


# topic=root.find(".//*[@TFD='UUID']").text
# print(topic)

#print([elem.tag for elem in root.iter()])
# print("*******************************************")
# for idx, movie in enumerate(root.iter('{http://www.pegasotecnologia.com/}TFD')):
# 	print(idx)
# 	print(movie.attrib)
# 	tfd=movie.attrib

# #tfd=root.iter('{http://www.pegasotecnologia.com/}TFD')
# print(tfd['UUID'])


# print("*******************************************")
# for idx, movie in enumerate(root.iter('{http://www.pegasotecnologia.com/}Transaccion')):
# 	print(idx)
# 	print(movie.attrib)
# 	tfd=movie.attrib

# #tfd=root.iter('{http://www.pegasotecnologia.com/}TFD')
# print(tfd['estatus'])



#0 .- {http://schemas.xmlsoap.org/soap/envelope/}Envelope || None
#1 .- {http://schemas.xmlsoap.org/soap/envelope/}Header || None
#2 .- {http://schemas.microsoft.com/2004/09/ServiceModel/Diagnostics}ActivityId || 00000000-0000-0000-0000-000000000000
#3 .- {http://schemas.xmlsoap.org/soap/envelope/}Body || None
#4 .- {http://namespace.pegasotecnologia.com/SCFD}emitirCFDResponse || None
#5 .- {http://namespace.pegasotecnologia.com/SCFD}emitirCFDResult || None
#6 .- {http://www.pegasotecnologia.com/}ResponseAdmon || None
#7 .- {http://www.pegasotecnologia.com/}Transaccion || None
#8 .- {http://www.pegasotecnologia.com/}CFD || None
#9 .- {http://www.pegasotecnologia.com/}TFD || None
print('********************************')
def response_cfdi_data(contents_xml,data_selector,info = True):
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
	return loop_atrib


def action_cfdi_date(parameter_date,current_date = True):
  if current_date:
      utcmoment_naive = datetime.utcnow()
  else:
      utcmoment_naive = parameter_date
  utcmoment = utcmoment_naive.replace(tzinfo=pytz.utc)
  satLocalFormat = "%Y-%m-%dT%H:%M:%S"
  satTimeZone = 'America/Mexico_City'
  localDatetime = utcmoment.astimezone(pytz.timezone(satTimeZone))
  satDateCFDI = localDatetime.strftime(satLocalFormat)
  return satDateCFDI

#print(response_cfdi_data(contents_xml,'TFD'))
print(response_cfdi_data(contents_xml,'Comprobante'))

print(action_cfdi_date(''))
