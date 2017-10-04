# -*- coding: utf-8 -*-

import odoo
from odoo import models, fields


class user_product(models.Model):
    _inherit = "product.template"

    # filtro de suscripcion
    type = fields.Selection(selection_add=[("sub", odoo._("Subscription"))])
