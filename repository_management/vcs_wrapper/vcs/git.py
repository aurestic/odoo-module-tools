# -*- coding: utf-8 -*-
# © 2016 Cristian Moncho <cristian.moncho@diagram.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# DOCS: https://github.com/gitpython-developers/GitPython

from datetime import datetime
import logging

from . import ABCVcs

try:
    import git
except ImportError:
    raise Exception('Git library not found.')

_logger = logging.getLogger(__name__)

try:
    if git.cmd.Git().version_info < (1, 7):
        _logger.warning(
            'Git version should be 1.7.0 or newer, some operations '
            'might not work as expected.')
except git.exc.GitCommandNotFound:
    raise Exception('Git is not installed.')


class Git(ABCVcs):
    _vcs = 'git'
    _dir_structure = ('.git',)

    def init(self, source, branch=None, **kwargs):
        _logger.debug('Initializing repo %s...', self._path)
        assert not self.is_initialized()
        self._repo = git.Repo.clone_from(source, self._path, **{
            'branch': branch, 'single-branch': True, 'depth': 1})

    def load(self, **kwargs):
        _logger.debug('Loading repo %s...', self._path)
        # Do not initialize if already initialized
        if not self._repo:
            assert self._path and self.is_repo(self._path)
            self._repo = git.Repo.init(self._path)

    def info(self):
        _logger.debug('Getting info from repo %s...', self._path)
        branch = self._repo.active_branch.name
        curr_rev = self._repo.rev_parse(branch)
        return dict(super(Git, self).info(), **{
            'source': self._repo.remotes.origin.url,
            'branch': branch,
            'rev_id': curr_rev.hexsha,  # [:7]
            # 'rev_date': datetime.fromtimestamp(curr_rev.authored_date),
            'rev_date': datetime.fromtimestamp(curr_rev.committed_date),
        })

    def update(self):
        # git fetch origin 8.0 && git reset --hard FETCH_HEAD
        _logger.debug('Updating repo %s...', self._path)
        assert self.is_initialized() and self.is_clean()
        branch = self._repo.active_branch
        # self._repo.git.pull('origin', branch.name, force=True)
        # self._repo.remote().pull(branch.name, force=True)
        # self._repo.remotes.origin.pull(branch.name, force=True)
        fetch_info = self._repo.remotes.origin.fetch(branch.name)
        branch.set_reference(fetch_info[0].ref.name)  # FETCH_HEAD

    def is_clean(self):
        return self.is_initialized() and \
            not self._repo.is_dirty(untracked_files=True)
