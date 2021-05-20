from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re


class Agreement(models.Model):
    _name = "library.agreement"
    _description = "Agreement"
    _inherit = 'mail.thread'

    agreement_name = fields.Char(
        string="Agreement name",
        help="The name of the agreement.",
        required=True,
    )

    library_ids = fields.Many2one(
        'library.library',
        required=True,
        string='Libraries')

    librarian_ids = fields.Many2one(
        'library.librarian',
        required=True,
        string='Librarians')

    agreement_file = fields.Many2many(
        'ir.attachment',
        'class_ir_attachments_rel',
        'class_id',
        'attachment_id',
        string="Agreement files",
        required=False)

    def name_get(self):
        name = []
        for record in self:
            name.append((
                record.id, record.agreement_name
            ))
        return name
