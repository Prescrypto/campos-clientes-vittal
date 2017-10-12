# -*- coding: utf-8 -*-

from odoo import models, fields, _


class partner_address(models.Model):
    _name = "partner.address"
    _inherit = "res.partner"

    # padre de la dirección
    parent_id = fields.Many2one("res.partner", string="Parent")

    # tipos de dirección
    address_type = fields.Selection(
        string="Address Type",
        selection=[("contact", _("Contact")),
                   ("coverage", _("Coverage Address")),
                   ("admin", _("Administrative Address")),
                   ("fiscal", _("Fiscal Address"))])

    # entre calles
    cross_street = fields.Char("Cross Streets")

    # referencias
    references = fields.Char("References")

    # fachada
    exterior = fields.Char("Exterior")

    # características especiales
    details = fields.Char("Details")
