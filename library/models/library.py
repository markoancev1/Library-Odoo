# -*- coding: utf-8 -*-
#
import logging

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
    _inherit = 'mail.thread',

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

    name_seq = fields.Char(
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

    library_description = fields.Text(
        string="Description",
        help="Description of the library.",
        required=True,
    )

    library_date = fields.Date(
        string="Establishment",
        help="The date when the library was established.",
        required=True
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

    @api.model
    def create(self, vals):
        if vals.get('name_seq', 'New') == 'New':
            vals['name_seq'] = self.env['ir.sequence'].next_by_code(
                'library.library.sequence') or 'New'
        result = super(Library, self).create(vals)
        return result

    @api.depends('library_librarian')
    def _num_of_librarians(self):
        for record in self:
            record.no_of_librarians = len(record.library_librarian)

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
            'domain': [('id','in', self.library_librarian.ids)],
            'target': 'current',
        }
