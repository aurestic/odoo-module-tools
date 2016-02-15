# -*- coding: utf-8 -*-
# © 2016 Cristian Moncho <cristian.moncho@diagram.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

_logger = logging.getLogger(__name__)
_LOADED_VCS = []


def load_vcs(vcs):
    vcs = vcs.lower()
    modname = 'vcs.%s' % (vcs,)
    clsname = vcs.title().replace('_', '')
    try:
        mod = getattr(__import__(modname, globals(), locals(), [], -1), vcs)
        return getattr(mod, clsname)
    except AttributeError:
        raise Exception(
            'Wrapper not found: from %s import %s' % (modname, clsname))


# [TODO] Automatically detect *.py files in 'vcs' folder
for vcs in ('git', 'bzr', 'hg', 'svn'):
    try:
        _LOADED_VCS.append((vcs, load_vcs(vcs)))
    except Exception as e:
        _logger.warning('Unable to load "%s" module: %s', vcs, e)

_logger.debug('Enabled VCS: %s', ', '.join(t[0] for t in _LOADED_VCS))


class VcsWrapper(object):
    """ Version Control System Wrapper. """
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
        """ Inspect the given path and search which VCS wrapper needs. """
        for vcs, cls in _LOADED_VCS:
            if cls.is_repo(path):
                return vcs
