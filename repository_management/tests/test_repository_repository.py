# -*- coding: utf-8 -*-

# ************
# *** TODO ***
# ************

import os

from openerp import exceptions
from openerp.tools import config
from openerp.tests.common import TransactionCase

from ..vcs_wrapper import VcsWrapper, test as vcs_wrapper_tests


class TestRepositoryRepository(TransactionCase):
    """ Test VCS compatibility """

    _VCS = VcsWrapper.available_vcs()
    _REPOSITORIES = {
        'git': [{
            'source': 'https://github.com/githubtraining/hellogitworld',
            'branch': 'master',
        }, {
            'source': 'https://github.com/OCA/server-tools',
            'branch': '8.0',
        }],
        'bzr': [{
            'source': 'lp:bzr-hello',
        }, {
            'source': 'http://bazaar.launchpad.net/~bzr/bzr-hello/trunk',
        }],
        'svn': [{
            'source': 'http://svn.red-bean.com/repos/test',
        }],
        'hg': [{
            'source': 'http://www.selenic.com/repo/hello',
            'branch': 'default',
        }],
    }

    def setUp(self):
        super(TestRepositoryRepository, self).setUp()

    def test_00_model(self):
        return  # TODO

        Dashboard = self.env['repository.dashboard']
        Repository = self.env['repository.repository']

        wizard_id = Dashboard.create({}).id

        for vcs in self._VCS[:1]:
            for vals in self._REPOSITORIES[vcs][:1]:
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

        vcs_wrapper_tests()
