# -*- coding: utf-8 -*-

from odoo import models, fields, api
from dateutil.relativedelta import relativedelta


class user_sales_order(models.Model):
    _inherit = "sale.order"

    # es suscripción?
    is_subscription = fields.Boolean("Subscription?", default=True)

    # fecha de inicio
    sub_start_date = fields.Date("Start of Subscription")

    # fecha de termino
    sub_end_date = fields.Date("End of Subscription")

    # recurrencia
    recurrence = fields.Selection(
        string="Recurrence",
        selection=[(1, "Monthly"), (2, "Bimonthly"), (6, "Semiannually"),
                   (12, "Yearly")])

    # fecha de siguiente facturación
    sub_invoice_date = fields.Date(compute="_add_month", store=True)

    @api.depends("sub_start_date", "sub_end_date", "recurrence")
    def _add_month(self):
        for record in self:
            if record.sub_start_date and record.recurrence:
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
