# -*- coding: utf-8 -*-
# © 2016 Cristian Moncho <cristian.moncho@diagram.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import os

from openerp import release
from openerp.tools.config import config, configmanager

_logger = logging.getLogger(__name__)


def repository_data_dir(self):
    d = os.path.join(self['data_dir'], 'repositories', release.series)
    if not os.path.exists(d):
        os.makedirs(d, 0o700)
    else:
        assert os.access(d, os.W_OK), \
            "%s: directory is not writable" % d
    return d

configmanager.repository_data_dir = property(repository_data_dir)

_logger.info('repositories path: %s', config.repository_data_dir)
