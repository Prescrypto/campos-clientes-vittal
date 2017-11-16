# -*- coding: utf-8 -*-

import odoo
import logging
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
import _sae as sae
from datetime import datetime
from functools import partial

_logger = logging.getLogger(__name__)


class user_sales_order(models.Model):
    _inherit = "sale.order"

    # es suscripción?
    is_subscription = fields.Boolean("Subscription?", default=False)

    # está activa la suscripción?
    sub_active = fields.Boolean("Subscription Active?", default=True)

    # comenzar suscripción
    def start_sub(self):
        for record in self:
            record.sub_start_date = fields.Datetime.to_string(datetime.now())
            record.sub_end_date = fields.Datetime.to_string(
                datetime.now() + relativedelta(months=12))
            record.sub_active = True

    # terminar suscripción
    def end_sub(self):
        for record in self:
            record.sub_start_date = fields.Datetime.to_string(datetime.now())
            record.sub_end_date = fields.Datetime.to_string(datetime.now())
            record.sub_active = False
            record.sub_start_date = ""
            record.sub_end_date = ""

    # fecha de inicio
    sub_start_date = fields.Date("Start of Subscription")

    # fecha de termino
    sub_end_date = fields.Date("End of Subscription")

    # recurrencia
    recurrence = fields.Selection(
        string="Recurrence",
        selection=[(1, odoo._("Monthly")), (2, odoo._("Bimonthly")),
                   (3, odoo._("Every 3 Months")), (6, odoo._("Semiannually")),
                   (12, odoo._("Yearly"))])

    # indicar si ya se genero la factura siguiente
    next_sub_invoiced = fields.Boolean("Invoiced?", default=False)

    # fecha de siguiente facturación de cron
    computed_invoice_date = fields.Date()

    # fecha de siguiente facturación
    sub_invoice_date = fields.Date(compute="_add_recurrence", store=True)

    @api.depends("sub_start_date", "sub_end_date", "computed_invoice_date", "recurrence")
    def _add_recurrence(self):
        for record in self:
            if record.sub_start_date and record.sub_end_date and record.recurrence:
                if record.computed_invoice_date:
                    record.sub_invoice_date = record.computed_invoice_date
                else:
                    # fecha de inicio a datetime
                    start = fields.Datetime.from_string(record.sub_start_date)
                    # fecha final a datetime
                    end = fields.Datetime.from_string(record.sub_end_date)
                    # calculo de siguiente facturación en base a recurrencia
                    calc = start + relativedelta(months=record.recurrence)
                    # si la fecha final es antes de la fecha calculada, usa la
                    # final, si no usa la calculada.
                    if end < calc:
                        record.sub_invoice_date = fields.Datetime.to_string(end)
                    else:
                        record.sub_invoice_date = fields.Datetime.to_string(calc)

    # pago automático
    auto_payment = fields.Boolean("Automatic Payment")

    # facturación automática
    auto_invoice = fields.Boolean("Automatic Invoicing", default=True)

    # recordatorio de pago
    auto_remind = fields.Boolean("Automatic Reminder")

    # renovacion de suscripción automatica
    auto_sub = fields.Boolean("Automatic Subscription Renewal")

    # zona derivada de contacto
    related_partner_zone = fields.Selection(
        string="Zone",
        related="partner_id.zone",
        readonly=True,
        company_dependent=True)

    partner_zone = fields.Char(string="Zone", compute="_get_zone", store=True)

    @api.depends("related_partner_zone")
    def _get_zone(self):
        for record in self:
            if record.related_partner_zone:
                record.partner_zone = record.related_partner_zone.upper()

    # id derivado de contacto
    related_partner_export_id = fields.Char(
        string="Partner ID",
        related="partner_id.client_export_id",
        readonly=True,
        company_dependent=True)

    partner_export_id = fields.Char(
        "Export ID", compute="_get_export_id", store=True)

    @api.depends("related_partner_export_id")
    def _get_export_id(self):
        for record in self:
            if record.related_partner_export_id:
                record.partner_export_id = record.related_partner_export_id

    # direccion de factura
    invoice_address_id = fields.Many2one("res.partner", string="Sale Address")

    # direccion de cobertura
    cov_address_id = fields.Many2one("res.partner", string="Coverage Address")

    @api.onchange("partner_id")
    def reset_address(self):
        self.invoice_address_id = None
        self.cov_address_id = None

    # fecha y hora de compromiso
    delivery_date = fields.Datetime("Delivery Date")

    # metodo invocado por cron para renovar suscripciones
    def _renew_subscription(self):
        for order in self.env['sale.order'].search([]):
            is_sub = order.is_subscription
            is_active = order.sub_active
            is_invoice = order.invoice_status == "invoiced" and order.state == 'sale'
            auto_invoice = order.auto_invoice
            has_ended = fields.Datetime.from_string(
                order.sub_invoice_date) < datetime.now(
                ) if order.sub_invoice_date else False
            been_invoiced = order.next_sub_invoiced

            if (is_sub and is_active and auto_invoice and has_ended
                    and is_invoice and not been_invoiced):
                _logger.info('crontab _renew_subscription')

                # calcular proxima fecha de facturación
                invoice_date = fields.Datetime.from_string(
                    order.sub_invoice_date)
                next_invoice_date = fields.Datetime.to_string(
                    invoice_date + relativedelta(months=order.recurrence))

                # indicar que la siguiente factura ya fue generada
                order.write({'next_sub_invoiced': True})

                # crear copia de factura con nueva fecha
                clone = order.copy(default={
                    'computed_invoice_date': next_invoice_date,
                    'next_sub_invoiced': False,
                    'invoice_status': 'invoiced',
                    'state': 'sale',
                })

                # guardar cambios en la base de datos
                self.env.cr.commit()

    def _renew_next_subscription(self):
        ''' Renueva la siguiente subscripción  si esta marcado próxima subs automática '''
        for order in self.env['sale.order'].search([]):
            # obtiene la instancia de la orden "order"
            _today = datetime.now()
            _end_date = fields.Datetime.from_string(order.sub_end_date)
            expire_today = True if (_today > _end_date) else False
            has_automatic_renew = order.auto_sub
            is_active = order.sub_active
            is_sub = order.is_subscription


            if expire_today and has_automatic_renew and is_active and is_sub:
                # Si expira este momento, tiene renovación automatica y es activa
                # Terminamos la order
                order.write({'sub_active': False})
                # TODO checar si hace falta más pasos para terminar la orden
                # Generar nuevas fechas
                _old_start_order = fields.Datetime.from_string(order.sub_start_date)
                _timelapse = _end_date - _old_start_order
                _start = _today + relativedelta(days=1)
                _end = _start + _timelapse

                # crear copia de factura con nueva fecha de subscripción
                clone = order.copy(default={
                    'state' : 'sale',
                    'sub_active' : True,
                    'sub_start_date' : fields.Datetime.to_string(_start),
                    'sub_end_date' : fields.Datetime.to_string(_end)
                })
                # save instance
                self.env.cr.commit()

            elif expire_today and not has_automatic_renew and is_active and is_sub:
                # Si su periodo(contrato) termino, pero no tenia automatica subscripción
                order.write({'sub_active': False})
                self.env.cr.commit()

    # ha sido facturada?
    exported = fields.Boolean("Exported?", default=False)

    # exportación sae
    def export(self):
        # encontrar ventas sin facturar ni exportar
        exported = self.env['sale.order'].search(
            [['invoice_status', '=', 'to invoice'],
             ['state', '=', 'sale'],
             ['exported', '=', False]])

        # actualizar fecha al momento de exportar
        exported.write({
            'create_date': fields.Datetime.to_string(datetime.now())
        })

        # query de sale_order con sale_order_lines
        exported.env.cr.execute("""
            SELECT
                sale.id as "Clave de Factura",
                partner.client_export_id as "Cliente",
                sale.create_date as "Fecha de elaboración (dia, mes, año)",
                '' as "Descuento financiero",
                item.name as "Observaciones",
                1 as "Clave de Vendedor",
                1 as "Su pedido",
                '' as "Fecha de entrega",
                '' as "Fecha de vencimiento",
                item.price_unit as "Precio",
                item.discount as "Desc. 1",
                0.00  as "Desc. 2",
                0.00 as "Desc. 3",
                '' as "Comisión",
                1 as "Clave de esquema de impuestos",
                product.clave_erste as "Clave del artículo",
                1 as "Cantidad",
                0 as "I.E.P.S",
                0 as "Impuesto 2",
                0 as "Impuesto 3",
                16 as "I.V.A.",
                sale.note as "Observaciones de partida"
            FROM sale_order_line item
            LEFT JOIN sale_order sale ON sale.id = item.order_id
            LEFT JOIN res_partner partner ON partner.id = sale.partner_id
            LEFT JOIN product_template product ON product.id = item.product_id
            WHERE
              sale.state = 'sale'
            AND
              sale.invoice_status = 'to invoice'
            AND
              sale.exported IS False;
        """)

        # valores del query
        rows = exported.env.cr.fetchall()

        # indicar que fueron exportados
        exported.write({'exported': True})

        # exportar
        format_orders = partial(sae.format, "orders")
        return map(format_orders, rows)
