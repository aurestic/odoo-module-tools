# -*- coding: utf-8 -*-
# © 2016 Cristian Moncho <cristian.moncho@diagram.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

import openerp
from openerp import api, fields, models

_logger = logging.getLogger(__name__)


class RepositoryRepositoryMessage(models.TransientModel):
    _name = 'repository.confirm'
    _description = 'Confirm Operation'

    state = fields.Selection([
        ('remove', 'Remove Repository'),
        ('update', 'Update Repository'),
        ('enable', 'Enable Repository'),
        ('disable', 'Disable Repository'),
    ], required=True, readonly=True)
    repository_id = fields.Many2one(
        'repository.repository', 'Repository', readonly=True)
    restart_server = fields.Boolean('Restart Server')
    update_module_list = fields.Boolean('Update Module List')

    @api.multi
    def action_confirm(self):
        self.ensure_one()
        res = {
            'remove': self.repository_id._action_remove,
            'update': self.repository_id._action_update,
            'enable': self.repository_id._action_enable,
            'disable': self.repository_id._action_disable,
        }.get(self.state)()

        if self.restart_server and self.update_module_list:
            menu_id = self._do_update_module_list('menu')
            res = self._do_restart_server(menu_id)
        elif self.restart_server:
            res = self._do_restart_server()
        elif self.update_module_list:
            res = self._do_update_module_list('action')

        return res

    def _do_restart_server(self, menu_id=None):
        if not menu_id:
            menu_id = self.env.ref('repository.repository_dashboard_menu').id
        self.env.cr.commit()
        openerp.service.server.restart()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
            'params': {
                'wait': True,
                'menu_id': menu_id,
            },
        }

    def _do_update_module_list(self, type):
        if type == 'menu':
            return self.env.ref('base.menu_view_base_module_update').id
        elif type == 'action':
            return self.env.ref(
                'base.action_view_base_module_update').read()[0]
