# -*- coding: utf-8 -*-

import csv
import io

from odoo import fields

import logging

_logger = logging.getLogger("============== EXPORT ==============")


def get_field(obj, field):
    if field is None:
        return ''
    data = field.split('@')
    field = data[0]
    f = False
    if len(data) == 2:
        f = data[1]
    if "const:" in field:
        return field.replace('const:', '').replace('"', '')
    elif "func:" in field:
        func = getattr(obj, field.replace('func:', ''))
        return func()
    else:
        value = None
        for n in field.split('.'):
            if value is None:
                value = getattr(obj, n)
            else:
                value = getattr(value, n)
        if isinstance(value, unicode):
            value = value.encode('utf-8', 'replace')
            # This fix the legacy invoice descriptions removing tabs or enters
            value = value.replace("\r"," ").replace("\t"," ").replace("\n"," ")
        if f and n == "date_invoice":
            #if the field is a date and the format is not false then get the value
            value =  fields.Date.from_string(value).strftime(f)

        return value if value else ''


def get_row(obj):
    em = obj.export_map
    row = []
    for v in em:
        row.append(get_field(obj, v))
    return row


def get_data(objects):
    if not objects or len(objects) < 1:
        return []
    values = []
    for o in objects:
        values.append(get_row(o))
    return values


def gen_csv(objects, header=True):
    output = io.BytesIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
    if header:
        writer.writerow(objects.header_map)
    values = get_data(objects)
    for v in values:
        writer.writerow(v)
    return output.getvalue()
