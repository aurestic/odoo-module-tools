# -*- coding: utf-8 -*-
# © 2016 Cristian Moncho <cristian.moncho@diagram.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import cgi
from docutils.core import publish_string
import logging
from lxml import etree
import os
import posixpath
import re
import shutil
import tempfile
import urllib
import urllib2
import urlparse
import zipfile

from openerp import api, exceptions, fields, models, modules, _
from openerp.tools import html_sanitize

from openerp.addons.base.module.module import MyWriter

_logger = logging.getLogger(__name__)
module_name_pattern = re.compile(r'[a-z]\w*', re.IGNORECASE)
url_list_separator = re.compile(r',|;|\s')


def load_information_from_zip(filepath):
    """ Return module name and description """
    terp = {}

    with zipfile.ZipFile(filepath, mode='r') as z:
        namelist = set(z.namelist())
        module = os.path.commonprefix(namelist).strip('/')

        if not module_name_pattern.match(module):
            raise exceptions.Warning(_(
                'Unable to get a valid module name: %s') % module)

        manifest = os.path.join(module, modules.module.MANIFEST)
        if manifest in namelist:
            tmpdir = tempfile.mkdtemp()
            try:
                z.extract(manifest, tmpdir)
                module_path = os.path.join(tmpdir, module)
                terp = modules.load_information_from_description_file(
                    module, module_path)
            finally:
                shutil.rmtree(tmpdir)
        else:
            _logger.warning("The module '%s' has no manifest file.")

    return module, terp


class ModuleExternalWizard(models.TransientModel):
    _name = 'module.external.wizard'
    _description = 'Module External'

    state = fields.Selection([
        ('select', 'Select'),
        ('confirm', 'Confirm'),
    ], required=True, default='select')

    url_list = fields.Text('URL List', states={
        'confirm': [('invisible', True)]})
    line_ids = fields.One2many(
        'module.external.wizard.line', 'wizard_id', 'Module Files')

    def _line_from_url(self, url):
        _logger.debug('Fetching %s...', url)
        res = urllib2.urlopen(url)

        # Get filename, see: http://stackoverflow.com/questions/11783269
        __, param = cgi.parse_header(res.info().get('content-disposition', ''))
        filename = param.get('filename')
        if not filename:
            filename = posixpath.basename(urlparse.urlsplit(url).path)

        return [(0, False, {
            'file': urllib2.urlopen(url).read().encode('base64'),
            'filename': filename,
        })]

    @api.multi
    def action_upload(self):
        self.ensure_one()

        if self.url_list:
            urls = url_list_separator.sub(',', self.url_list).split(',')
            line_vals = []
            for url in filter(None, urls):  # Skip empty elements
                try:
                    line_vals += self._line_from_url(url)
                except Exception as e:
                    raise exceptions.Warning(
                        _('Unable to get module from %s:\n%s') % (url, e))
            # TODO: Direct asignment (self.line_ids = line_vals) is not
            # correctly working, does not set the field `wizard_id`
            self.write({'line_ids': line_vals})

        # self.line_ids.filtered(lambda r: not r.active).unlink()
        # if self.line_ids:
        self.state = 'confirm'
        return {
            'name': _(self._description),
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id,
            'res_model': self._name,
            'type': 'ir.actions.act_window',
            'context': self.env.context,
        }

    @api.multi
    def action_confirm(self):
        self.ensure_one()
        urls = {}

        for line in self.line_ids:
            if line.module in urls:
                raise exceptions.Warning('Modules cannot be declared twice.')

            # Path as URL, see: http://stackoverflow.com/questions/11687478
            urls[line.module] = urlparse.urljoin(
                'file:', urllib.pathname2url(line.filepath))

        if urls:
            return self.env['ir.module.module'].with_context(**{
                'force_internal_path': True
            }).install_from_urls(urls)


class ModuleExternalWizardLine(models.TransientModel):
    _name = 'module.external.wizard.line'

    wizard_id = fields.Many2one(
        'module.external.wizard', 'Wizard', required=True, ondelete='cascade')

    active = fields.Boolean('Active', readonly=True, default=True)
    file = fields.Binary(
        'File', compute='_compute_file', inverse='_inverse_file')
    filename = fields.Char('File Name', required=True)
    filepath = fields.Char('File Path', readonly=True)
    module = fields.Char('Module', readonly=True)
    version = fields.Char('Version', readonly=True)
    description = fields.Text('Description', readonly=True)
    description_html = fields.Html(
        'Description HTML', compute='_compute_description_html')

    @api.multi
    def _compute_file(self):
        for rec in self:
            if rec.filepath and os.path.isfile(rec.filepath):
                with open(rec.filepath, 'rb') as f:
                    rec.file = f.read().encode('base64')

    @api.multi
    def _inverse_file(self):
        for rec in self:
            if rec.file:
                try:
                    with tempfile.NamedTemporaryFile(delete=False) as f:
                        f.write(rec.file.decode('base64'))
                        rec.filepath = f.name
                    rec.module, terp = load_information_from_zip(rec.filepath)
                    rec.description = terp.get('description', '')
                    rec.version = terp.get('version', '')
                except Exception as e:
                    # raise exceptions.Warning(
                    #     _("Unable to read '%s':\n%s") % (rec.filename, e))
                    _logger.warning('Unable to read %s: %s', rec.filename, e)
                    rec.active = False

    @api.multi
    @api.depends('description')
    def _compute_description_html(self):
        for rec in self:
            overrides = {
                'embed_stylesheet': False,
                'doctitle_xform': False,
                'output_encoding': 'unicode',
                'xml_declaration': False,
            }
            rec.description_html = html_sanitize(publish_string(
                source=rec.description or '', settings_overrides=overrides,
                writer=MyWriter()))

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.filepath and os.path.isfile(rec.filepath):
                os.unlink(rec.filepath)
                _logger.debug('The file %s has been cleaned up.', rec.filepath)
        return super(ModuleExternalWizardLine, self).unlink()

    @api.model
    def fields_view_get(
            self, view_id=None, view_type=False, toolbar=False, submenu=False):
        res = super(ModuleExternalWizardLine, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)

        if self.env.context.get('wizard_state') == 'confirm' and \
                view_type == 'tree':
            doc = etree.XML(res['arch'])
            doc.xpath("//tree")[0].attrib['create'] = 'false'
            del doc.xpath("//tree")[0].attrib['editable']
            res['arch'] = etree.tostring(doc)

        return res
