# -*- coding: utf-8 -*-

from odoo import models, fields, _


class partner_address(models.Model):
    _name = "partner.address"
    _inherit = "res.partner"

    # padre de la dirección
    parent_id = fields.Many2one("res.partner", string="Parent")

    # miembros de clientes que usan la direccion para domicilio de atención
    family_atte_address = fields.One2many(
        "family.member", "atte_address_id", string="Attention Address")

    company_atte_address = fields.One2many(
        "company.member", "atte_address_id", string="Attention Address")

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
