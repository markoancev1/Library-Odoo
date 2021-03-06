# -*- coding: utf-8 -*-
#
import logging
from odoo.tools import email_split, email_escape_char
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re

COUNTRIES = [
    ("1", "Macedonia"),
    ("2", "Serbia"),
    ("3", "Croatia")
]

email_pattern = r'^[_a-z0-9-]+(\.[_a-z0-9-]+)*' \
                r'@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$'


class Library(models.Model):
    _name = "library.library"
    _description = "Library"
    _inherit = 'mail.thread', 'mail.activity.mixin'

    _sql_constraints = [
        ('unique_librarian',
         'unique(library_name, '
         'library_country)',
         'The Library you are trying to enter '
         'has already been entered with the same information.'),
        ('unique_library_email',
         'unique(library_email)',
         'The email has already been taken by another library.')
    ]

    library_seq = fields.Char(
        string="ID",
        readonly=True,
        required=True,
        copy=False,
        default='New')

    library_image = fields.Binary(
        string="Image"
    )

    library_name = fields.Char(
        string="Name",
        help="The name of the library.",
        required=True,
    )

    library_date = fields.Date(
        'Created Date',
        required=True,
        default=fields.Date.today()
    )

    library_description = fields.Text(
        string="Description",
        help="Description of the library.",
        required=True,
    )

    library_country = fields.Selection(
        COUNTRIES,
        string="Country",
        help="Country of the library.",
        required=True,
        track_visibility="onchange",
        default=COUNTRIES[0][0]
    )

    library_email = fields.Char(
        string="Email",
        help="Email of the library",
        required=True
    )

    library_librarian = fields.Many2many(
        "library.librarian",
        "library_librarian_rel",
        "librarian_library",
        "library_librarian",
        string="Librarians",
        required=False
    )

    agreement = fields.One2many(
        'library.agreement',
        'library_ids',
        required=False,
        readonly=True,
        string='Agreements')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('public', 'Public'),
        ('private', 'Private'),
    ], string='Status',
        readonly='True',
        default='draft',
        track_visibility="onchange"
    )

    no_of_librarians = fields.Integer(
        compute='_num_of_librarians',
        string="Number of librarians",
        help="How many librarians are in the library",
        default=0,
        track_visibility="onchange"
    )

    no_of_agreements = fields.Integer(
        compute='_num_of_agreements',
        string="Number of agreements",
        default=0,
    )

    @api.model
    def create(self, vals):
        if vals.get('library_seq', 'New') == 'New':
            vals['library_seq'] = self.env['ir.sequence'].next_by_code(
                'library.library.sequence') or 'New'
        result = super(Library, self).create(vals)
        return result

    @api.depends('library_librarian')
    def _num_of_librarians(self):
        for record in self:
            record.no_of_librarians = len(record.library_librarian)

    @api.depends('agreement')
    def _num_of_agreements(self):
        for record in self:
            record.no_of_agreements = len(record.agreement)

    def name_get(self):
        name = []
        for record in self:
            name.append((
                record.id, record.library_name
            ))
        return name

    @api.constrains('library_name')
    def _check_name(self):
        for record in self:
            if len(record.library_name) < 3:
                raise ValidationError(
                    "The library's name should have at least 3 characters."
                )

    @api.constrains('library_description')
    def _check_lastname(self):
        for record in self:
            if len(record.library_description) < 20:
                raise ValidationError(
                    "The library's description "
                    "should have at least 20 characters."
                )

    @api.constrains('library_email')
    def _check_email(self):
        for record in self:
            if record.library_email:
                match = re.match(email_pattern, record.library_email)
                if match is None:
                    raise ValidationError(
                        'The email you have entered is not valid.'
                    )

    @api.onchange('public_library')
    def print_state(self):
        logging.info(self.library_librarian.ids)
        logging.info("alert")

    def action_public(self):
        for record in self:
            record.state = "public"

    def action_private(self):
        for record in self:
            record.state = "private"

    def action_show_librarians(self):
        self.ensure_one()
        return {
            'name': _('Librarians'),
            'view_mode': 'tree,form',
            'res_model': 'library.librarian',
            'type': 'ir.actions.act_window',
            'context': {'create': False, 'delete': False},
            'domain': [('id', 'in', self.library_librarian.ids)],
            'target': 'current',
        }

    def action_show_agreements(self):
        self.ensure_one()
        return {
            'name': _('Agreements'),
            'view_mode': 'tree,form',
            'res_model': 'library.agreement',
            'type': 'ir.actions.act_window',
            'context': {'create': False, 'delete': False},
            'domain': [('id', 'in', self.agreement.ids)],
            'target': 'current',
        }

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        self = self.with_context(default_user_id=False)
        if custom_values is None:
            custom_values = {}
        regex = re.compile("^\[(.*)\]")
        match = regex.match(msg_dict.get('subject')).group(1)
        book_id = self.env['library.book'].search([('name', '=', match), ('state', '=', 'available')], limit=1)
        custom_values['book_id'] = book_id.id
        email_from = email_escape_char(email_split(msg_dict.get('from'))[0])
        custom_values['borrower_id'] = self._search_on_partner(email_from)
        return super(Library, self).message_new(msg_dict, custom_values)
