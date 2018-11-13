# -*- coding: utf-8 -*-

import simple_export as se
from odoo import models, fields, api

import logging

_logger = logging.getLogger("============== EXPORT ==============")


class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    
    exported = fields.Boolean("¿Exportado?", readonly=True, default=False, copy=False,
        help="Este campo indica si la factura ya fue exportada.")
    
    # exportación sae
    def export(self):
        orders = self.env['account.invoice'].search(
            [('exported', '=', False), ('state', 'in', ('open', 'paid'))]
        )
        export_lines = ""
        for o in orders:
            export_lines = export_lines + se.gen_csv(o.invoice_line_ids, header=False)
        header = se.gen_csv(self.env['account.invoice.line'])
        orders.write({'exported': True})
        orders.write({'invoice_id': 1})
        self.env.cr.commit()
        return header + export_lines

    @api.multi
    def export_all(self):
        export_lines = ""
        for o in self:
            export_lines = export_lines + se.gen_csv(o.invoice_line_ids, header=False)
        header = se.gen_csv(self.env['account.invoice.line'])
        self.env.cr.commit()
        return header + export_lines


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    product_id = fields.Many2one('product.product', required=True)

    export_map = [
        'id',
        'invoice_id.partner_id.group_code',
        'invoice_id.date_invoice@%d/%m/%y',
        None,
        None,
        None,
        None,
        'invoice_id.comment',
        'invoice_id.user_id.id',
        'invoice_id.id',
        None,
        'invoice_id.date_due@%d/%m/%y',
        'price_unit',
        'const:0',
        'const:0',
        'const:0',
        'const:0',
        None,
        'product_id.default_code',
        'quantity',
        None,
        'func:get_ret_isr',
        'func:get_ret_iva',
        'func:get_iva',
        None,
        'name',
        'invoice_id.sat_metodo_pago',
        'invoice_id.sat_pagos_id.nombre_forma',
        'invoice_id.sat_uso_id.nombre_uso'
    ]

    # Obtiene el porcentaje de retención de ISR
    def get_ret_isr(self):
        for tax in self.invoice_line_tax_ids:
            if 'RET ISR' in tax.name:
                return -tax.amount
        return ''

    # Obtiene el porcentaje de retención de IVA
    def get_ret_iva(self):
        for tax in self.invoice_line_tax_ids:
            if 'RET IVA' in tax.name:
                return -tax.amount
        return ''

    # Obtiene el IVA
    def get_iva(self):
        for tax in self.invoice_line_tax_ids:
            if tax.name in ['IVA(0%) VENTAS','IVA(16%) VENTAS']:
                return tax.amount
        return ''

    header_map = [
        'Clave',
        'Cliente',
        'Fecha de elaboración',
        'Descuento financiero',
        'Numero de almacen cabecera',
        'Numero de Moneda',
        'Tipo de Cambio',
        'Observaciones',
        'Clave de vendedor',
        'Su pedido',
        'Fecha de entrega',
        'Fecha de vencimiento',
        'Precio',
        'Desc. 1',
        'Desc. 2',
        'Desc. 3',
        'Comisión',
        'Clave de esquema de impuestos',
        'Clave del artículo',
        'Cantidad',
        'I.E.P.S.',
        'Ret. ISR',
        'Ret. IVA',
        'I.V.A.',
        'Numero de almacen Partidas',
        'Observaciones de partida',
        'Metodo de Pago',
        'Forma de Pago Sat',
        'Uso CFDI'
    ]
