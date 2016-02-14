# -*- coding: utf-8 -*-
# © 2016 Cristian Moncho <cristian.moncho@diagram.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Repository Management',
    'summary': 'Manage external repositories.',
    'version': '8.0.1.0',
    'category': 'Administration',
    'author': 'Cristian Moncho',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'external_dependencies': {
        'bin': ['git'],
        'python': ['git'],
    },
    'depends': [
        'base',
    ],
    'data': [
        'views/repository_dashboard_view.xml',
        'views/repository_repository_view.xml',
        'wizard/repository_clone_view.xml',
        'wizard/repository_confirm_view.xml',
    ],
}
