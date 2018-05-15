# -*- coding: utf-8 -*-

from odoo import models, fields


class SatPagos(models.Model):
    _name = "sat.pagos"

    _rec_name = "nombre_forma"

    nombre_forma = fields.Char(string="Forma de pago")

    codigo_forma = fields.Char(string="Código de pagos")

    bancarizado = fields.Char("Bancarizado")

    numero_operacion = fields.Char("Número de Operación")

    rfc_emisor = fields.Char("RFC del Emisor")

    cuenta_ordenante = fields.Char("Cuenta Ordenante")

    patron_ordenante = fields.Char("Patrón para Cuenta Ordenante")

    rfc_beneficiario = fields.Char("RFC del Emisor Cuenta del Beneficiario")

    cuenta_beneficiario = fields.Char("Cuenta de Beneficiario")

    patron_beneficiario = fields.Char("Patrón para Cuenta Beneficiaria")

    tipo_cadena = fields.Char("Tipo Cadena Pago")

    nombre_banco = fields.Char("Nombre del Banco")

    inicio_vigencia = fields.Date("Fecha Fin de Vigencia")

    fin_vigencia = fields.Date("Fecha Inicio de Vigencia")

    sat_pagos_ids = fields.One2many(
        "res.partner", "sat_pagos_id", string="Formas de Pago")
