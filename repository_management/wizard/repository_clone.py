# -*- coding: utf-8 -*-
# © 2016 Cristian Moncho <cristian.moncho@diagram.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from openerp import api, fields, models, release

from ..vcs_wrapper import VcsWrapper

_logger = logging.getLogger(__name__)

SELECTION_VCS = [(i, i) for i in VcsWrapper.available_vcs()]
DEFAULT_VCS = SELECTION_VCS[0][0] if SELECTION_VCS else None


class RepositoryRepositoryClone(models.TransientModel):
    _name = 'repository.clone'

    vcs = fields.Selection(
        SELECTION_VCS, 'VCS', default=DEFAULT_VCS, required=True)
    source = fields.Char('Source', required=True)
    branch = fields.Char('Branch', default=release.series)

    @api.multi
    def action_clone(self):
        self.ensure_one()
        self.env['repository.repository'].with_context(**{
            'initialize_repository': True
        }).create({
            'vcs': self.vcs,
            'source': self.source,
            'branch': self.branch,
        })
