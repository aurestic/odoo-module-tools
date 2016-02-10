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

{
    'name': 'Repository Management',
    'summary': 'Manage external repositories.',
    'author': 'Cristian Moncho',
    'version': '8.0.1.0',
    'license': 'AGPL-3',
    'depends': [
        'base',
    ],
    'data': [
        'views/repository_dashboard_view.xml',
        'views/repository_repository_view.xml',
        'wizard/repository_clone_view.xml',
        'wizard/repository_confirm_view.xml',
    ],
    'installable': False,
}
