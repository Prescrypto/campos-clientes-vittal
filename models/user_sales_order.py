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

