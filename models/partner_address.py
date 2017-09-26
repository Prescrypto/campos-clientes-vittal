# -*- coding: utf-8 -*-

import odoo
from odoo import models, fields


class partner_address(models.Model):
    _name = 'partner.address'
    _inherit = 'res.partner'

    # padre de la dirección
    parent_id = fields.Many2one(
        'res.partner', string="Parent", ondelete="set null")

    # tipos de dirección
    address_type = fields.Selection(
        string="Address Type",
        help="Group addresses",
        selection=[('admin', odoo._('Administrative Address')),
                   ('fiscal', odoo._('Fiscal Address')),
                   ('coverage',
                    odoo._('Coverage Address')), ('attention',
                                                  odoo._('Support Address'))])

    # entre calles
    cross_street = fields.Char(
        string="Cross Streets", help="Nearest intersection")

    # referencias
    references = fields.Char(
        string="References", help="Nearby landmarks or reference points")

    # fachada
    exterior = fields.Char(
        string="Exterior", help="Description of exterior of address")

    # características especiales
    details = fields.Char(
        string="Details", help="Special details or characteristics")

    # establecer como domicilio de atención default
    default_address = fields.Boolean(
        string="Default Address", help="Default address for the group")
