# -*- coding: utf-8 -*-

import odoo
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta


class user_client(models.Model):
    _inherit = 'res.partner'

    # direcciones del grupo
    address_ids = fields.One2many(
        'partner.address', 'parent_id', string="Addresses")

    # miembros del grupo
    member_ids = fields.One2many(
        'partner.member', 'parent_id', string='Members')

    # código de grupo
    group_id = fields.Selection(
        string="Group Code",
        help="Internal group code",
        selection=[('area_p', 'AREA-P'), ('conv', 'CONV'),
                   ('evento', 'EVENTO'), ('grupos', 'GRUPOS'), ('otros',
                                                                'OTROS')])

    group_name = fields.Char(compute="_group_name", store=True)

    @api.depends('group_id')
    def _group_name(self):
        for record in self:
            if record.group_id:
                record.group_name = {
                    'area_p': odoo._('Protected Areas'),
                    'conv': odoo._('Agreements'),
                    'evento': odoo._('Events'),
                    'grupos': odoo._('Groups'),
                    'otros': odoo._('Other')
                }.get(record.group_id, odoo._('None Selected'))

    # código postal de colonia
    zip_extra = fields.Char(string="Zip Extra", help="Extended zip code")

    # tipo de usuario adicional
    client_type = fields.Selection(selection=[('company', 'Company'),
                                              ('family', 'Family'),
                                              ('individual', 'Individual')])

    # nombre comercial
    legal_name = fields.Char(
        string="Legal Name", help="Legal or fiscal name of business")

    # rfc
    rfc = fields.Char(string="RFC", help="RFC Code")

    # lada de país
    country_code = fields.Char(
        string="Country Code", help="Telephone country code")

    # código de zona
    zone = fields.Selection(
        string="Zone",
        help="Zone code",
        selection=[('bqelms', 'BQELMS'), ('itrlms', 'ITRLMS'),
                   ('lomas', 'LOMAS'), ('plnco', 'PLNCO'), ('sfe', 'SFE'),
                   ('tcmchl', 'TCMCHL'), ('unica', 'UNICA')])

    # código de producto
    product_custom_id = fields.Char(string="Product Code", help="Product code")

    # cápitas
    quantity = fields.Integer(string="Quantity", help="Quantity in group")

    # fechas de suscripción
    sub_duration = fields.Integer('Duration', default=1)

    sub_start_date = fields.Date(
        string="Start of Subscription", help="Date when subscription started")

    sub_end_date = fields.Date(compute="_add_month", store=True)

    @api.depends('sub_start_date', 'sub_duration')
    def _add_month(self):
        for record in self:
            if record.sub_start_date:
                start_fmt = fields.Datetime.from_string(record.sub_start_date)
                endtime = start_fmt + relativedelta(months=record.sub_duration)
                record.sub_end_date = fields.Datetime.to_string(endtime)

    # hogar protegido
    protected_home_auto = fields.Boolean(
        compute="_protected_home_auto", store=True, readonly=True)

    @api.depends('quantity')
    def _protected_home_auto(self):
        for record in self:
            if record.quantity > 4:
                record.protected_home_auto = True

    protected_home_user = fields.Boolean(
        string='Protected Home', help="Protected home program")

    protected_home = fields.Boolean(compute="_protected_home", store=True)

    @api.depends('protected_home_auto', 'protected_home_user')
    def _protected_home(self):
        for record in self:
            if record.protected_home_auto or record.protected_home_user:
                record.protected_home = True


class partner_member(models.Model):
    _name = 'partner.member'
    _inherit = 'res.partner'

    # número de socio
    member_id = fields.Char(
        string="Associate ID", help="Unique identifier for associates")

    # padre del miembro
    parent_id = fields.Many2one(
        'res.partner', string="Parent", ondelete="set null")

    # titular del grupo
    is_owner = fields.Boolean(string="Owner", help="Is this the owner")

    # condición de grupo
    relationship = fields.Selection(
        string="Relationship",
        help="Type of member",
        selection=[("1", "Spouse"), ("3", "Offspring"), ("4", "Other family"),
                   ("9", "Not family")])

    # fecha de nacimiento
    birthday = fields.Date(string="Birthday", help="Date of birth")


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

