# -*- coding: utf-8 -*-
# © 2016 Cristian Moncho <cristian.moncho@diagram.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# DOCS: https://github.com/dsoprea/PySvn

from __future__ import absolute_import

import logging

from . import ABCVcs, which

# The "svn" module cannot be imported if Subversion is not installed
try:
    which('svn', exc=True)
except:
    raise Exception('Subversion is not installed.')

try:
    import svn.remote
    import svn.local
except ImportError:
    raise Exception('Subversion library not found.')

_logger = logging.getLogger(__name__)


class Svn(ABCVcs):
    _vcs = 'svn'
    _dir_structure = ('.svn',)

    def init(self, source, branch=None, **kwargs):
        assert not self.is_initialized()
        _logger.debug('Initializing repo %s...', self._path)
        repo = svn.remote.RemoteClient(source)
        repo.checkout(self._path)

    def load(self, **kwargs):
        assert self._path and self.is_repo(self._path)
        _logger.debug('Loading repo %s...', self._path)
        self._repo = svn.local.LocalClient(self._path)

    def info(self):
        _logger.debug('Getting info from repo %s...', self._path)
        repo_info = self._repo.info()
        return dict(super(Svn, self).info(), **{
            'source': repo_info['url'],
            # 'branch': None,
            'rev_id': repo_info['commit_revision'],
            'rev_date': repo_info['commit_date'],
        })

    def update(self):
        assert self.is_initialized() and self.is_clean()
        _logger.debug('Updating repo %s...', self._path)
        self._repo.run_command('update', [self._path])

    def is_clean(self):
        """ True if there are no changes and no new files. """
        if not self.is_initialized():
            return False
        return not filter(None, self._repo.run_command('status', [self._path]))
