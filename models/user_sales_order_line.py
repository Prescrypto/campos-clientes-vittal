# -*- coding: utf-8 -*-

from odoo import models, fields, api


class user_sales_order_line(models.Model):
    _inherit = "sale.order.line"

    # estado derivado de orden
    related_state = fields.Selection(
        string="Order State",
        related="order_id.state",
        readonly=True,
        company_dependent=True)

    state = fields.Char(
        "State", compute="_get_order_state", store=True)

    @api.depends("related_state")
    def _get_order_state(self):
        for record in self:
            if record.related_state:
                record.state = record.related_state

    # clave erste derivada de producto
    related_product_code = fields.Char(
        string="Product Code",
        related="product_id.clave_erste",
        readonly=True,
        company_dependent=True)

    product_code = fields.Char(
        "Product Code", compute="_get_product_code", store=True)

    @api.depends("related_product_code")
    def _get_product_code(self):
        for record in self:
            if record.related_product_code:
                record.product_code = record.related_product_code
