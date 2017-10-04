# -*- coding: utf-8 -*-

import odoo
from odoo import models, fields


class partner_address(models.Model):
    _name = "partner.address"
    _inherit = "res.partner"

    # padre de la dirección
    parent_id = fields.Many2one("res.partner", string="Parent")

    # tipos de dirección
    address_type = fields.Selection(
        string="Address Type",
        selection=[("admin", odoo._("Administrative Address")),
                   ("fiscal", odoo._("Fiscal Address")),
                   ("coverage",
                    odoo._("Coverage Address")), ("attention",
                                                  odoo._("Support Address"))])

    # entre calles
    cross_street = fields.Char("Cross Streets")

    # referencias
    references = fields.Char("References")

    # fachada
    exterior = fields.Char("Exterior")

    # características especiales
    details = fields.Char("Details")

    # establecer como domicilio de atención default
    default_address = fields.Boolean("Default Address")
