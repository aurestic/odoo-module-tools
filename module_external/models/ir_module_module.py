# -*- coding: utf-8 -*-
# © 2016 Cristian Moncho <cristian.moncho@diagram.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class IrModuleModule(models.Model):
    _inherit = 'ir.module.module'

    @api.model
    def get_apps_server(self):
        if self.env.context.get('force_internal_path'):
            return 'file://'
        return super(IrModuleModule, self).get_apps_server()
