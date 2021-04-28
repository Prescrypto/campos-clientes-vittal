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

    @api.multi
    def stamp_all_cfdi(self):
        print("pass by ****************")
        for line in self:
            if not line.sat_pegaso_uuid:
                print("Selected invoices: {}".format(line) )
                line.write({'sat_pegaso_response': "response.text" })
                self.action_invoice_cfdi(line)

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    product_id = fields.Many2one('product.product', required=True)

    export_map = [
        'id', #clave
        'invoice_id.partner_id.group_code', #cliente
        'invoice_id.date_invoice@%d/%m/%y', #fecha de elaboracion
        'invoice_id.comment', #observaciones
        'invoice_id.user_id.id', #clave de vendedor
        'invoice_id.id', #su pedido
        None, #fecha de entrega
        'invoice_id.date_due@%d/%m/%y', #fecha de vencimiento
        'price_unit', #precio
        'const:0', #desc 1
        'const:0', #desc 2
        'const:0', # desc 3
        'const:0', #comision
        'invoice_line_tax_ids.tax_group_id.id', #clave de esquema de impuestos
        'product_id.default_code', #clave del articulo
        'quantity', #cantidad
        None, # ieps
        'func:get_ret_isr', #impuesto 2
        'func:get_ret_iva', #impuesto 3
        'func:get_iva', #iva
        'name', #observaciones de partida
        'invoice_id.sat_metodo_pago', #metodo de pago
        'invoice_id.sat_pagos_id.codigo_forma', #forma de pago sat
        'invoice_id.sat_uso_id.codigo_uso' #uso cfdi
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
        'Impuesto 2',
        'Impuesto 3',
        'I.V.A.',
        'Observaciones de partida',
        'Metodo de Pago',
        'Forma de Pago Sat',
        'Uso CFDI'
    ]

