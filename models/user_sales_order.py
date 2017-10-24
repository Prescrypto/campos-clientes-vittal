# -*- coding: utf-8 -*-

import odoo
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from datetime import datetime


class user_sales_order(models.Model):
    _inherit = "sale.order"

    # es suscripción?
    is_subscription = fields.Boolean("Subscription?", default=False)

    # está activa la suscripción?
    sub_active = fields.Boolean("Subscription Active?")

    # comenzar suscripción
    @api.multi
    def start_sub(self):
        for record in self:
            record.sub_start_date = fields.Datetime.to_string(datetime.now())
            record.sub_end_date = fields.Datetime.to_string(
                datetime.now() + relativedelta(months=12))
            record.sub_active = True

    # terminar suscripción
    @api.multi
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

    # fecha de siguiente facturación
    sub_invoice_date = fields.Date(compute="_add_recurrence", store=True)

    @api.multi
    @api.depends("sub_start_date", "sub_end_date", "recurrence")
    def _add_recurrence(self):
        for record in self:
            if record.sub_start_date and record.sub_end_date and record.recurrence:
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
    auto_invoice = fields.Boolean("Automatic Invoicing")

    # recordatorio de pago
    auto_remind = fields.Boolean("Automatic Reminder")

    # renovacion de suscripción automatica
    auto_sub = fields.Boolean("Automatic Subscription Renewal")

    # zona derivada de dirección
    related_partner_zone = fields.Selection(
        string="Zone",
        related="partner_id.zone",
        readonly=True,
        company_dependent=True)

    partner_zone = fields.Char(string="Zone", compute="_get_zone", store=True)

    @api.multi
    @api.depends("related_partner_zone")
    def _get_zone(self):
        for record in self:
            if record.related_partner_zone:
                record.partner_zone = record.related_partner_zone.upper()

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

