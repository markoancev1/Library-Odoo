# -*- coding: utf-8 -*-
#
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re

email_pattern = r'^[_a-z0-9-]+(\.[_a-z0-9-]+)*' \
                r'@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$'


class Librarian(models.Model):
    _name = "library.librarian"
    _description = "Librarian"
    _inherit = 'mail.thread'

    _sql_constraints = [
        ('unique_librarian',
         'unique(librarian_firstname, '
         'librarian_lastname, '
         'librarian_date)',
         'The Librarian you are trying to enter '
         'has already been entered with the same information.'),
        ('unique_librarian_email',
         'unique(librarian_email)',
         'The email has already been taken by another librarian.')
    ]

    librarian_seq = fields.Char(
        string="ID",
        readonly=True,
        required=True,
        copy=False,
        default='New')

    librarian_image = fields.Binary(
        string="Image"
    )

    librarian_firstname = fields.Char(
        string="Firstname",
        help="The firstname of the librarian.",
        required=True,
    )
    librarian_lastname = fields.Char(
        string="Lastname",
        help="The lastname of the librarian.",
        required=True,
    )
    librarian_email = fields.Char(
        string="Email",
        help="The email of the librarian.",
        required=True,
    )
    librarian_date = fields.Date(
        string="Birthdate",
        help="The date when the librarian was conceded.",
        required=True,
    )
    librarian_library = fields.Many2many(
        "library.library",
        "library_librarian_rel",
        "library_librarian",
        "librarian_library",
        string="Libraries",
        required=False,
        readonly=True
    )

    agreement = fields.One2many(
        'library.agreement',
        'librarian_ids',
        required=False,
        readonly=True,
        string='Agreements')

    no_of_libraries = fields.Integer(
        compute='_num_of_libraries',
        string="Number of libraries",
        help="How many libraries is the librarian a part off",
        default=0
    )

    no_of_agreements = fields.Integer(
        compute='_num_of_agreements',
        string="Number of agreements",
        default=0
    )

    @api.model
    def create(self, vals):
        if vals.get('librarian_seq', 'New') == 'New':
            vals['librarian_seq'] = self.env['ir.sequence'].next_by_code(
                'library.librarian.sequence') or 'New'
        result = super(Librarian, self).create(vals)
        return result

    @api.depends('librarian_library')
    def _num_of_libraries(self):
        for record in self:
            record.no_of_libraries = len(record.librarian_library)

    @api.depends('agreement')
    def _num_of_agreements(self):
        for record in self:
            record.no_of_agreements = len(record.agreement)

    def name_get(self):
        name = []
        for record in self:
            name.append((
                record.id, record.librarian_firstname +
                ' ' + record.librarian_lastname
            ))
        return name

    @api.constrains('librarian_firstname')
    def _check_name(self):
        for record in self:
            if len(record.librarian_firstname) < 3:
                raise ValidationError(
                    "Librarian first name should have at least 3 characters."
                )

    @api.constrains('librarian_lastname')
    def _check_lastname(self):
        for record in self:
            if len(record.librarian_lastname) < 5:
                raise ValidationError(
                    "Librarian last name should have at least 5 characters."
                )

    @api.constrains('librarian_email')
    def _check_email(self):
        for record in self:
            if record.librarian_email:
                match = re.match(email_pattern, record.librarian_email)
                if match is None:
                    raise ValidationError(
                        "The email you have entered is not valid."
                    )

    def action_show_libraries(self):
        self.ensure_one()
        return {
            'name': _('Libraries'),
            'view_mode': 'tree,form',
            'res_model': 'library.library',
            'type': 'ir.actions.act_window',
            'context': {'create': False, 'delete': False},
            'domain': [('id', 'in', self.librarian_library.ids)],
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
