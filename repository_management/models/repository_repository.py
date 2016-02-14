# -*- coding: utf-8 -*-
# © 2016 Cristian Moncho <cristian.moncho@diagram.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re
import os
from os.path import isfile
from os.path import join as path_join
import logging

from openerp import api, exceptions, fields, models, _
from openerp.tools import config

from ..vcs_wrapper import VcsWrapper

_logger = logging.getLogger(__name__)
filename_sanitize = re.compile(r'[^0-9a-zA-Z]+')


def find_modules(path):
    """ Return all module names inside the given path. """
    return [module for module in os.listdir(path) if any(map(
        lambda f: isfile(path_join(path, module, f)), (
            '__openerp__.py', '__terp__.py')))]


def build_repository_path(vcs, source, branch=None, **kwargs):
    """ Generates the repository full path. """
    basedir = '%(test)s%(vcs)s_%(source)s%(branch)s' % {
        'test': 'test_' if kwargs.get('test') else '',
        'vcs': vcs,
        'source': source,
        'branch': '_%s' % (branch,) if branch else '',
    }
    return path_join(
        config.repository_data_dir, filename_sanitize.sub('_', basedir))


class RepositoryRepository(models.TransientModel):
    _name = 'repository.repository'
    _description = 'Repository'
    _rec_name = 'source'
    # _order = 'source ASC'

    wizard_id = fields.Many2one(
        'repository.dashboard', 'Dashboard', required=True, readonly=True)
    path = fields.Char('Path', required=True, readonly=True)
    vcs = fields.Char('VCS', required=True, readonly=True)
    source = fields.Char('Source', required=True, readonly=True)
    branch = fields.Char('Branch', readonly=True)  # default=release.series,
    rev_id = fields.Char('Last Revision', readonly=True)
    rev_date = fields.Datetime('Last Rev. Date', readonly=True)
    dirty = fields.Boolean('Dirty', readonly=True)

    enabled = fields.Boolean('Enabled', compute='_compute_repository')

    module_ids = fields.Many2many(
        'ir.module.module', string='Modules', compute='_compute_repository')
    module_count = fields.Integer('# Modules', compute='_compute_repository')

    @api.multi
    @api.depends('path')
    def _compute_repository(self):
        Module = self.env['ir.module.module']
        curr_addons_path = set(config['addons_path'].split(','))
        for rec in self:
            rec.enabled = rec.path in curr_addons_path
            if rec.enabled:
                module_names = find_modules(rec.path)
                rec.module_ids = Module.search([('name', 'in', module_names)])
                rec.module_count = len(rec.module_ids)

    @api.model
    def create(self, vals):
        if self.env.context.get('initialize_repository'):
            vals['path'] = build_repository_path(**vals)
            try:
                vals = VcsWrapper.from_source(**vals).info()
            except Exception as e:
                raise exceptions.Warning(_(
                    "An error has occurred while fetching '%s':\n%s") % (
                        vals['source'], e))
        return super(RepositoryRepository, self).create(vals)

    @api.multi
    def copy(self, default=None):
        raise exceptions.Warning(_(
            'Repository duplication is not allowed, please create a new one.'))

    @api.multi
    def unlink(self):
        if self.env.context.get('remove_repository'):
            for rec in self:
                if rec.enabled:
                    raise exceptions.Warning(
                        _('Unable to remove an enabled repository.'))
                VcsWrapper.from_dir(rec.vcs, rec.path).remove()
        return super(RepositoryRepository, self).unlink()

    @api.multi
    def action_open_modules(self):
        """ Show repository modules. """
        self.ensure_one()
        return {
            'name': self.source,
            'type': 'ir.actions.act_window',
            'res_model': 'ir.module.module',
            'view_type': 'form',
            'view_mode': 'kanban,tree,form',
            'target': 'current',
            'domain': [('id', 'in', self.module_ids.ids)]
        }

    @api.multi
    def action_confirm(self):
        RepositoryConfirm = self.env['repository.confirm']
        action = self.env.context.get('action')
        KNOWN_ACTIONS = {'remove', 'update', 'enable', 'disable'}

        if action not in KNOWN_ACTIONS:
            raise exceptions.Warning(_('Unkown action: %s') % (action,))

        if not self.env.user.has_group('base.group_system'):
            raise exceptions.AccessDenied

        return {
            'name': _(RepositoryConfirm._description),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'repository.confirm',
            'res_id': RepositoryConfirm.create({
                'repository_id': self.id,
                'state': action
            }).id
        }

    @api.multi
    def action_confirm_remove(self):
        return self.with_context(action='remove').action_confirm()

    @api.multi
    def action_confirm_update(self):
        return self.with_context(action='update').action_confirm()

    @api.multi
    def action_confirm_enable(self):
        return self.with_context(action='enable').action_confirm()

    @api.multi
    def action_confirm_disable(self):
        return self.with_context(action='disable').action_confirm()

    @api.multi
    def _action_remove(self):
        self.ensure_one()

        if not self.env.user.has_group('base.group_system'):
            raise exceptions.AccessDenied

        try:
            self.with_context(remove_repository=True).unlink()
        except Exception as e:
            raise exceptions.Warning(_(
                "An error has occurred while deleting '%s':\n%s") % (
                    self.source, e))

        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def _action_update(self):
        self.ensure_one()

        if not self.env.user.has_group('base.group_system'):
            raise exceptions.AccessDenied

        if self.dirty:
            raise exceptions.Warning(
                _('It is discouraged to enable non-clean repositories.'))

        try:
            VcsWrapper.from_dir(self.vcs, self.path).update()
        except Exception as e:
            raise exceptions.Warning(_(
                "An error has occurred while updating '%s':\n%s") % (
                    self.source, e))

    @api.multi
    def _action_enable(self):
        self.ensure_one()

        if not self.env.user.has_group('base.group_system'):
            raise exceptions.AccessDenied

        addons_path = config['addons_path'].split(',')
        if config._is_addons_path(self.path) and self.path not in addons_path:
            # if self.dirty:
            #     raise exceptions.Warning(
            #         _('It is discouraged to enable non-clean repositories.'))
            # Must be inserted at the beginning to ensure max load priority,
            # this way localization modules can be overridden
            addons_path.insert(0, self.path)
            config['addons_path'] = ','.join(addons_path)
            config.save()

    @api.multi
    def _action_disable(self):
        self.ensure_one()

        if not self.env.user.has_group('base.group_system'):
            raise exceptions.AccessDenied

        addons_path = config['addons_path'].split(',')
        if self.path in addons_path:
            if self.module_ids.filtered(lambda r: r.state not in (
                    'uninstalled', 'uninstallable')):
                raise exceptions.Warning(
                    _('The repository contains installed modules.'))
            addons_path.remove(self.path)
            config['addons_path'] = ','.join(addons_path)
            config.save()
