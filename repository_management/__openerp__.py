# -*- coding: utf-8 -*-
# © 2016 Cristian Moncho <cristian.moncho@diagram.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Repository Management',
    'summary': 'Manage external repositories.',
    'author': 'Cristian Moncho',
    'version': '8.0.1.0',
    'license': 'AGPL-3',
    'depends': [
        'base',
    ],
    'external_dependencies': {
        'bin': ['git'],
        'python': ['git'],
    },
    'data': [
        'views/repository_dashboard_view.xml',
        'views/repository_repository_view.xml',
        'wizard/repository_clone_view.xml',
        'wizard/repository_confirm_view.xml',
    ],
    'installable': False,
}
