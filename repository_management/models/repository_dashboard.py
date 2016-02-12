# -*- coding: utf-8 -*-
# © 2016 Cristian Moncho <cristian.moncho@diagram.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import os
from os.path import join as path_join
from os.path import isdir, basename, normpath

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
    _description = 'Repository Dashboard'

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
