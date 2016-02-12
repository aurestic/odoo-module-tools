# -*- coding: utf-8 -*-

import logging
import os

from openerp import exceptions
from openerp.tools import config
from openerp.tests.common import TransactionCase

from ..vcs_wrapper import VcsWrapper

_logger = logging.getLogger(__name__)


class TestRepositoryRepository(TransactionCase):
    """ Test VCS compatibility """

    _LOADED_VCS = VcsWrapper.available_vcs()
    _REPOSITORIES = [
        ('git', [{
            'source': 'https://github.com/crimoniv/odoo-module-tools',
            'branch': '8.0',
        }, {
            'source': 'https://github.com/githubtraining/hellogitworld',
            'branch': 'master',
        }, ]),
        ('bzr', [{
            'source': 'lp:bzr-hello',
        }, {
            'source': 'http://bazaar.launchpad.net/~bzr/bzr-hello/trunk',
        }]),
        ('svn', [{
            'source': 'http://svn.red-bean.com/repos/test',
        }]),
        ('hg', [{
            'source': 'http://www.selenic.com/repo/hello',
            'branch': 'default',
        }]),
    ]

    def setUp(self):
        super(TestRepositoryRepository, self).setUp()

    def test_00_orm(self):
        return  # TODO

        MAX_VCS = 1
        MAX_REPOS = 1

        Dashboard = self.env['repository.dashboard']
        Repository = self.env['repository.repository']

        wizard_id = Dashboard.create({}).id

        for vcs in self._LOADED_VCS[:MAX_VCS]:
            for vals in dict(self._REPOSITORIES)[vcs][:MAX_REPOS]:
                vals['wizard_id'] = wizard_id

                # Initialize (new)
                with self.assertRaises(Exception):
                    Repository.create(vals)
                repo = Repository.with_context(
                    initialize_repository=True).create(vals)
                self.assertTrue(os.path.isdir(repo.path), 'MSG')
                self.assertTrue(os.listdir(repo.path), 'MSG')
                self.assertEqual(repo.branch, vals.get('branch'), 'MSG')
                self.assertFalse(repo.dirty, 'MSG')

                # Initialize (existing)
                Repository.create({
                    'path': repo.path,
                    'vcs': repo.vcs,
                    'source': repo.source,
                    'branch': repo.branch,
                }).unlink()

                # Update
                dummy_file = os.path.join(repo.path, '.deleteme.test')
                with open(dummy_file, 'a'):
                    pass
                with self.assertRaises(AssertionError):
                    repo._action_update()
                os.unlink(dummy_file)
                repo._action_update()

                # Enable
                self.assertNotIn(repo.path, config['addons_path'], 'MSG')
                repo._action_enable()
                self.assertIn(repo.path, config['addons_path'], 'MSG')

                # Delete (1)
                with self.assertRaises(exceptions.Warning):
                    repo.with_context(remove_repository=True).unlink()

                # Disable
                repo._action_disable()
                self.assertNotIn(repo.path, config['addons_path'], 'MSG')

                # Delete (2)
                repo.with_context(remove_repository=True).unlink()
                self.assertFalse(os.path.isdir(repo.path), 'MSG')

    def test_20_vcs_wrapper(self):
        return  # TODO

        import shutil
        import tempfile
        from pprint import pformat

        success = True
        tmp_dir = tempfile.mkdtemp()

        try:
            for vcs, repos in self._REPOSITORIES:
                if vcs not in self._LOADED_VCS:
                    _logger.warning('"%s" support is not enabled.', vcs)
                    continue

                for repo in repos:
                    _logger.info('Testing "%s" with %s', vcs, repo)
                    repo_dir = tempfile.mkdtemp(dir=tmp_dir)

                    try:
                        _logger.info('* Testing "from_source"...')
                        test1 = VcsWrapper.from_source(vcs, repo_dir, **repo)
                        self.asserTrue(test1.is_initialized(), 'MSG')

                        _logger.info('* Testing "from_dir" (no guess)...')
                        test2 = VcsWrapper.from_dir(vcs, repo_dir)
                        self.asserTrue(test2.is_initialized(), 'MSG')

                        _logger.info('* Testing "from_dir" (guess)...')
                        test3 = VcsWrapper.from_dir(None, repo_dir)
                        self.asserTrue(test3.is_initialized(), 'MSG')

                        _logger.info('* Testing "info"...')
                        info = test3.info()
                        _logger.info('\n' + pformat(test3.info(), width=1))
                        self.assertEquals(info['vcs'], vcs, 'MSG')

                        _logger.info('* Testing "update"...')
                        test2.update()

                        _logger.info('* Testing "remove"...')
                        test3.remove()
                        self.assertFalse(os.path.isdir(repo['path']), 'MSG')
                    except Exception as e:
                        _logger.warning(e)
                        success = False
        finally:
            if success:
                _logger.info('Result: All tests passed!')
            else:
                _logger.warning('Result: Some tests failed.')

            if tmp_dir and os.path.isdir(tmp_dir):
                shutil.rmtree(tmp_dir)
