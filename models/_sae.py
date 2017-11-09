# -*- coding: utf-8 -*-

from re import findall, sub
from odoo import fields
import unicodedata


# formatea datos exportados de odoo a sae
def format(type, row):
    # format client data
    if type == 'clients':
        row = format_clients(row)
    elif type == 'products':
        row = format_products(row)
    elif type == 'orders':
        row = format_orders(row)

    # limpiar datos
    return sanitize(row)


# formatea datos de productos
def format_orders(row):
    # extraer id numerico de string
    row[0] = extract_id(row[0])
    # formatear datetime
    row[2] = date_format(row[2])
    # agregar campos no exportados
    row.insert(3, "")
    row.insert(5, "1")
    row.insert(6, "1")
    # formatear datetime
    row[7] = date_format(row[7])
    row[8] = date_format(row[8])
    # agregar campos no exportados
    for index in range(10, 14):
        row.insert(index, "0")
    row.insert(14, "1")
    # agregar codigo indicando exportación
    row.insert(15, "IMPORTADO")
    # agregar campos no exportados
    row.insert(16, "1")
    for index in range(17, 20):
        row.insert(index, "0")
    row.insert(20, "16")
    row.insert(21, "")
    return row


# formatea datos de productos
def format_products(row):
    # extraer id numerico de string
    row[0] = extract_id(row[0])
    # agregar campos no exportados
    for index in range(2, 18):
        row.insert(index, "")
    # agregar campos no exportados
    for index in range(19, 26):
        row.insert(index, "")
    # agregar clave de esquema
    row.insert(26, "1")
    # agregar campos no exportados
    for index in range(27, 31):
        row.insert(index, "")
    # agregar campos no exportados
    for index in range(32, 37):
        row.insert(index, "")
    # agregar campos no exportados
    for index in range(40, 45):
        row.insert(index, "")
    return row


# formatea datos de cliente
def format_clients(row):
    # variable no mutadas
    street = row[3]
    # agregar estatus
    row.insert(1, "")
    # extraer id numerico de string
    row[0] = extract_id(row[0])
    # extraer nombre de calle
    row[3] = extract_street(row[3])
    # extraer interior de calle y agregar a lista
    row.insert(4, extract_interior(street))
    # agregar clasificación
    row.insert(18, "")
    # agregar campo no exportados
    row.insert(22, "")
    # agregar campo de imprimir
    row.insert(23, "N")
    # agregar campo de correo electronico
    row.insert(24, "S")
    # agregar campos no exportados
    for index in range(25, 43):
        row.insert(index, "")
    # agregar campo de tipo de empresa
    row.insert(43, "M")
    for index in range(44, 69):
        row.insert(index, "")
    row.insert(70, "")
    row.insert(71, "")
    for index in range(73, 75):
        row.insert(index, "")
    for index in range(77, 79):
        row.insert(index, "")
    return row


# extraer id numerico
def extract_id(id):
    return id.split('.')[-1].split('_')[-1]


# extraer numero interior de campo calle
def extract_interior(street):
    interior = findall('\d+', street)
    return interior[0] if interior else ""


# extraer nombre de calle de campo de calle
def extract_street(street_with_interior):
    street = sub('(\d+)', "", street_with_interior).lstrip()
    return street if street else ""


# limpiar datos
def sanitize(row):
    # quitar comas para no romper csv
    clean_row = map(
        lambda r: r.replace(",", " ") if isinstance(r, basestring) else r, row)
    # Normaliza los campos, quita acentos y caracteres no soportados
    normalize_row = map(lambda r: unicodedata.normalize("NFKD", u'{}'.format(r) ).encode('ascii', "ignore"), clean_row)
    # regresar renglon corregido, removiendo valores falsos
    return map(lambda r: r if r else "", normalize_row)


# formatear fechas
def date_format(date_string):
    date = fields.Datetime.from_string(date_string)
    return date.strftime('%d/%m/%Y') if date else ""
