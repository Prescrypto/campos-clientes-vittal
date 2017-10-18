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
    @api.one
    def start_sub(self):
        self.sub_start_date = fields.Datetime.to_string(datetime.now())
        self.sub_end_date = fields.Datetime.to_string(datetime.now() +
                                                      relativedelta(months=12))
        self.sub_active = True

    # terminar suscripción
    @api.one
    def end_sub(self):
        self.sub_start_date = fields.Datetime.to_string(datetime.now())
        self.sub_end_date = fields.Datetime.to_string(datetime.now())
        self.sub_active = False
        self.sub_start_date = ""
        self.sub_end_date = ""

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

    @api.one
    @api.depends("sub_start_date", "sub_end_date", "recurrence")
    def _add_recurrence(self):
        if self.sub_start_date and self.sub_end_date and self.recurrence:
            # fecha de inicio a datetime
            start = fields.Datetime.from_string(self.sub_start_date)
            # fecha final a datetime
            end = fields.Datetime.from_string(self.sub_end_date)
            # calculo de siguiente facturación en base a recurrencia
            calc = start + relativedelta(months=self.recurrence)
            # si la fecha final es antes de la fecha calculada, usa la
            # final, si no usa la calculada.
            if end < calc:
                self.sub_invoice_date = fields.Datetime.to_string(end)
            else:
                self.sub_invoice_date = fields.Datetime.to_string(calc)

    # pago automático
    auto_payment = fields.Boolean("Automatic Payment")

    # facturación automática
    auto_invoice = fields.Boolean("Automatic Invoicing")

    # recordatorio de pago
    auto_remind = fields.Boolean("Automatic Reminder")

    # renovacion de suscripción automatica
    auto_sub = fields.Boolean("Automatic Subscription Renewal")

    # direccion de factura
    invoice_address_id = fields.Many2one(
        "partner.address", string="Sale Address")

    # direccion de cobertura
    coverage_address_id = fields.Many2one(
        "partner.address", string="Coverage Address")

    # fecha y hora de compromiso
    delivery_date = fields.Datetime("Delivery Date")

