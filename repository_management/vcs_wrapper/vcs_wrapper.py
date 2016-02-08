#!/usr/bin/env python2
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

import inspect
from os.path import isdir as is_dir
import logging

_logger = logging.getLogger(__name__)
_LOADED_VCS = []

if __name__ == '__main__':
    import sys
    fmt = '%(asctime)-15s %(levelname)s - %(message)s'
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format=fmt)


def load_vcs(vcs):
    module = 'vcs.%s' % (vcs,)
    pred = lambda c: inspect.isclass(c) and c.__module__.endswith(module)
    args = (module, globals(), locals(), [], -1)
    cls = inspect.getmembers(getattr(__import__(*args), vcs), pred)
    if len(cls) != 1:
        raise Exception('Main class not found.')
    return cls[0][1]


# [TODO] Automatically detect *.py files in 'vcs' folder
for vcs in ('git', 'bzr', 'hg', 'svn'):
    try:
        _LOADED_VCS.append((vcs, load_vcs(vcs)))
    except Exception as e:
        _logger.warning('Unable to load "%s" module: %s', vcs, e)

_logger.debug('Enabled VCS: %s', ', '.join(t[0] for t in _LOADED_VCS))


class VcsWrapper(object):
    """Version Control System classes' wrapper.

    [TODO]
    """
    def __new__(cls, vcs, path, **kwargs):
        if not vcs:
            vcs = cls._guess_vcs(path)

        try:
            return dict(_LOADED_VCS)[vcs](path, **kwargs)
        except KeyError:
            raise Exception('Unknown repository structure in %s' % (path,))

    @classmethod
    def available_vcs(cls):
        return zip(*_LOADED_VCS)[0] if _LOADED_VCS else ()

    @classmethod
    def from_source(cls, vcs, path, source, branch=None, **kwargs):
        res = cls(vcs, path)
        res.init(source, branch=branch, **kwargs)
        res.load()
        return res

    @classmethod
    def from_dir(cls, vcs, path, **kwargs):
        res = cls(vcs, path)
        res.load(**kwargs)
        return res

    @staticmethod
    def _guess_vcs(path):
        """ [TODO] """
        for vcs, cls in _LOADED_VCS:
            if cls.is_repo(path):
                return vcs

def test():
    import shutil
    import tempfile
    from pprint import pformat

    test_repos = [
        ('git', [{
            'source': 'https://github.com/githubtraining/hellogitworld',
            'branch': 'master',
        }, {
            'source': 'https://github.com/OCA/server-tools',
            'branch': '8.0',
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

    success = True
    tmp_dir = None
    try:
        tmp_dir = tempfile.mkdtemp()

        for vcs, repos in test_repos:
            if vcs not in dict(_LOADED_VCS):
                _logger.warning('*** The "%s" management is not enabled', vcs)
                continue

            for repo in repos:
                _logger.info('*** Testing "%s" with %s', vcs, repo)
                repo_dir = tempfile.mkdtemp(dir=tmp_dir)

                try:
                    _logger.info('* Testing "from_source"...')
                    _logger.info('Initializing...')
                    test1 = VcsWrapper.from_source(vcs, repo_dir, **repo)
                    _logger.info('Initialized!')

                    _logger.info('* Testing "from_dir" (no guess)...')
                    _logger.info('Loading...')
                    test2 = VcsWrapper.from_dir(vcs, test1.path)
                    _logger.info('Loaded!')
                    _logger.info('Updating...')
                    test2.update()
                    _logger.info('Updated!')

                    _logger.info('* Testing "from_dir" (guess)...')
                    test3 = VcsWrapper.from_dir(None, test1.path)
                    _logger.info('Guessed type: %s', test3.vcs)

                    _logger.info(
                        '* Repo data:\n' + pformat(test3.info(), width=1))

                    _logger.info('* Removing repo...')
                    test3.remove()
                    _logger.info('Removed!')
                except Exception as e:
                    _logger.warning(e)
                    success = False
    finally:
        if success:
            _logger.info('*** Result: All tests passed!')
        else:
            _logger.warning('*** Result: Some tests have failed.')

        _logger.info('*** Cleanup')
        if tmp_dir and is_dir(tmp_dir):
            _logger.info('* Cleaning tmp dir %s...', tmp_dir)
            shutil.rmtree(tmp_dir)

if __name__ == '__main__':
    test()
