# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class BusinessType(models.Model):
    _name = 'business.type'

    name = fields.Char('Business Type', required=True, unique=True)
    description = fields.Text('Description')
