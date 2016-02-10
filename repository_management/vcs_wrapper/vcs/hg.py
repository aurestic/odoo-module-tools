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

# see: https://www.mercurial-scm.org/wiki/PythonHglib
# see: https://selenic.com/repo/python-hglib

from __future__ import absolute_import

import logging

from . import ABCVcs, which

try:
    import hglib
except ImportError:
    raise Exception('Mercurial library not found.')

# The "hglib" module does not work correctly if Mercurial is not installed
try:
    # hglib.client.hgclient(None, None, None).version
    which('hg', exc=True)
except:
    raise Exception('Mercurial is not installed.')

_logger = logging.getLogger(__name__)


class Hg(ABCVcs):
    _vcs = 'hg'
    _dir_structure = ('.hg',)

    def init(self, source, branch=None, **kwargs):
        _logger.debug('Initializing repo %s...', self._path)
        assert not self.is_initialized()
        branch = branch or 'default'
        hglib.clone(source, self._path, branch=branch)

    def load(self, **kwargs):
        _logger.debug('Loading repo %s...', self._path)
        assert self._path and self.is_repo(self._path)
        self._repo = hglib.open(self._path)

    def info(self):
        _logger.debug('Getting info from repo %s...', self._path)
        branch = self._repo.branch()
        tip = self._repo.tip()
        return dict(super(Hg, self).info(), **{
            'source': self._repo.paths()[branch],
            'branch': branch,
            'rev_id': tip[1],  # [:12]
            'rev_date': tip[-1],
        })

    def update(self):
        assert self.is_initialized() and self.is_clean()
        _logger.debug('Updating repo %s...', self._path)
        self._repo.update()

    def is_clean(self):
        """ True if there are no changes and no new files. """
        return self.is_initialized() and not self._repo.status()
