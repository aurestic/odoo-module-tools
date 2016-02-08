# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    This module copyright:
#        (C) 2016 Cristian Moncho
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging

from openerp import api, fields, models, release

from ..vcs_wrapper import VcsWrapper

_logger = logging.getLogger(__name__)

_SELECTION_VCS = [(i, i) for i in VcsWrapper.available_vcs()]
_DEFAULT_VCS = _SELECTION_VCS[0][0] if _SELECTION_VCS else None


class RepositoryRepositoryClone(models.TransientModel):
    _name = 'repository.clone'

    vcs = fields.Selection(
        _SELECTION_VCS, 'VCS', default=_DEFAULT_VCS, required=True)
    source = fields.Char('Source', required=True)
    branch = fields.Char('Branch', default=release.series)

    @api.multi
    def action_clone(self):
        self.ensure_one()
        Repository = self.env['repository.repository']
        Repository.with_context(**{
            'initialize_repository': True
        }).create({
            'vcs': self.vcs,
            'source': self.source,
            'branch': self.branch,
        })
