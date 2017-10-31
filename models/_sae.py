# -*- coding: utf-8 -*-

from re import findall, sub


# formatea datos exportados de odoo a sae
def format(type, row):
    # format client data
    if type == 'clients':
        row = format_clients(row)
    elif type == 'products':
        row = format_products(row)

    # limpiar datos
    return sanitize(row)


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
    # agregar campos no exportados
    for index in range(22, 68):
        row.insert(index, "")
    row.insert(69, "")
    row.insert(70, "")
    for index in range(72, 77):
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

    # regresar renglon corregido, removiendo valores falsos
    return map(lambda r: r if r else "", clean_row)
