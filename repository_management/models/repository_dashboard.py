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

import os
from os.path import join as path_join
from os.path import isdir, basename, normpath
import logging

from openerp import api, exceptions, fields, models, _
from openerp import release
from openerp.tools import config

from ..vcs_wrapper import VcsWrapper

_logger = logging.getLogger(__name__)


def repository_dir(*args):
    """ /home/<user>/.local/share/Odoo/repositories/<version> """
    d = path_join(
        config['data_dir'], 'repositories', release.series, *args)
    if not isdir(d):
        os.makedirs(d, 0o700)
    assert os.access(d, os.W_OK), '%s: directory is not writable' % (d,)
    return d


def abslistdirs(d):
    for f in os.listdir(d):
        res = path_join(d, f)
        if isdir(res):
            yield res


def deduplicate_list(l):
    """ .. see:: http://stackoverflow.com/questions/7961363 """
    return [i for n, i in enumerate(l) if i not in l[:n]]


def get_repository_paths():
    FORBIDDEN_NAMES = set([release, 'addons'])
    paths = config['addons_path'].split(',')
    paths = filter(
        lambda p: basename(normpath(p)) not in FORBIDDEN_NAMES, paths)
    return deduplicate_list(paths + list(abslistdirs(repository_dir())))

_logger.debug('Repository dir: %s', repository_dir())


class RepositoryDashboard(models.TransientModel):
    _name = 'repository.dashboard'

    name = fields.Char('Name', default=lambda s: _('Repositories'))
    repository_ids = fields.One2many(
        'repository.repository', 'wizard_id', 'Repositories',
        default=lambda self: self._default_repository_ids())

    def _default_repository_ids(self):
        """ Find all repositories. """
        res = []

        for path in get_repository_paths():
            _logger.debug('Inspecting %s...', path)
            try:
                res.append((0, False, VcsWrapper.from_dir(None, path).info()))
            except:
                _logger.warning(
                    "The directory '%s' does not contain a valid repository "
                    "structure." % (path,))
        return res

    @api.multi
    def copy(self, default=None):
        raise exceptions.Warning(_('Dashboard duplication is not allowed.'))

    @api.multi
    def action_add_repository(self):
        return {
            'name': _('Clone Repository'),
            'type': 'ir.actions.act_window',
            'res_model': 'repository.clone',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_wizard_id': self.id
            },
        }
