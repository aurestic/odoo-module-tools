# -*- coding: utf-8 -*-
# © 2016 Cristian Moncho <cristian.moncho@diagram.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# DOCS: https://www.mercurial-scm.org/wiki/PythonHglib
# DOCS: https://selenic.com/repo/python-hglib

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
