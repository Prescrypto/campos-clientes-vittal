# -*- coding: utf-8 -*-

from odoo import models, fields


class user_product(models.Model):
    _inherit = "product.template"

    # filtro de suscripcion
    type = fields.Selection(selection_add=[('sub', 'Subscription')])
