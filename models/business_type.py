# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class BusinessType(models.Model):
    _name = 'business.type'

    name = fields.Char('Tipo de negocio', required=True, unique=True)
    description = fields.Text('Descripción')
