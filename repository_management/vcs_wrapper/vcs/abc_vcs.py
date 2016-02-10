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

from __future__ import absolute_import

import shutil
from abc import ABCMeta, abstractmethod
from os.path import isdir as is_dir
from os.path import join as path_join
from distutils import spawn
import logging

_logger = logging.getLogger(__name__)


def which(cmd, exc=False):
    """ Return the executable full path or 'None'. """
    path = spawn.find_executable(cmd)
    if not path and exc:
        raise CommandNotFound(cmd)
    return path


class CommandNotFound(Exception):
    pass


class LocallyModifiedError(Exception):
    pass


class ABCVcs(object):
    """An Abstract Base Class for Version Control System classes.

    [TODO]
    """
    __metaclass__ = ABCMeta

    _vcs = None
    _path = None
    _repo = None

    def __init__(self, path):
        self._path = path

    @abstractmethod
    def init(self, **kwargs):
        """ Initialize repository into dir from source. """
        pass

    @abstractmethod
    def load(self, **kwargs):
        """ Load repository from dir. """
        pass

    @abstractmethod
    def update(self):
        """ Update repository to the latest revision. """
        pass

    @abstractmethod
    def is_clean(self):
        """ Test if there are no changes and no new files. """
        pass

    @classmethod
    def is_repo(cls, path):
        """ Determine if 'path' has a valid repository structure. """
        return path and is_dir(path_join(path, *cls._dir_structure))

    @property
    def vcs(self):
        return self._vcs

    @property
    def path(self):
        return self._path

    def info(self):
        """ Returns all the repository known info. """
        return {
            'vcs': self._vcs,
            'path': self._path,
            'source': None,
            'branch': None,
            'rev_id': None,
            'rev_date': None,
            'dirty': not self.is_clean(),
        }

    def remove(self):
        """ Remove repository from file system. """
        if self.is_initialized() and not self.is_clean():
            raise LocallyModifiedError
        if self._path and is_dir(self._path):
            shutil.rmtree(self._path)
            _logger.info('The repository %s has been removed.', self._path)

    def is_initialized(self):
        """ [DEPRECATED] Test if repository is initialized. """
        return not not self._repo
