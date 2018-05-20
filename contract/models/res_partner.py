# -*- coding: utf-8 -*-
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api

import logging

_log = logging.getLogger("========== CONTRATOS =============")


class ResPartner(models.Model):
    _inherit = 'res.partner'

    contract_count = fields.Integer(
        string='Contracts',
        compute='_compute_contract_count',
    )

    # Obtener ultimo contrato del cliente
    last_contract = fields.Many2one('account.analytic.account', string='Último contrato', compute='_get_last_contract', store=False)

    @api.multi
    def _get_last_contract(self):
        for partner in self:
            contracts = self.env['account.analytic.account'].sudo().search([('partner_id', '=', partner.id)], order="id desc")
            if len(contracts) > 0:
                _log.info("%s" % contracts)
                partner.last_contract = contracts[0]
            else:
                partner.last_contract = None

    def _compute_contract_count(self):
        Contract = self.env['account.analytic.account']
        today = fields.Date.today()
        for partner in self:
            partner.contract_count = Contract.search_count([
                ('recurring_invoices', '=', True),
                ('partner_id', '=', partner.id),
                ('date_start', '<=', today),
                '|',
                ('date_end', '=', False),
                ('date_end', '>=', today),
            ])

    def act_show_contract(self):
        """ This opens contract view
            @return: the contract view
        """
        self.ensure_one()
        res = self.env['ir.actions.act_window'].for_xml_id(
            'contract', 'action_account_analytic_overdue_all')
        res.update(
            context=dict(
                self.env.context,
                search_default_recurring_invoices=True,
                search_default_not_finished=True,
                default_partner_id=self.id,
                default_recurring_invoices=True,
            ),
            domain=[('partner_id', '=', self.id)],
        )
        return res
