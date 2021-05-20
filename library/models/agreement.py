from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re


class Agreement(models.Model):
    _name = "library.agreement"
    _description = "Agreement"
    _inherit = 'mail.thread'

    agreement_seq = fields.Char(
        string="ID",
        readonly=True,
        required=True,
        copy=False,
        default='New')

    agreement_name = fields.Char(
        string="Name",
        help="The name of the agreement.",
        required=True,
    )

    library_ids = fields.Many2one(
        'library.library',
        required=True,
        track_visibility="onchange",
        string='Libraries')

    librarian_ids = fields.Many2one(
        'library.librarian',
        required=True,
        track_visibility="onchange",
        string='Librarians')

    agreement_file = fields.Many2many(
        'ir.attachment',
        'class_ir_attachments_rel',
        'class_id',
        'attachment_id',
        string="Agreement files",
        required=False)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
    ], string='Status',
        readonly='True',
        default='draft',
        track_visibility="onchange"
    )

    def action_approved(self):
        for record in self:
            record.state = "approved"

    def action_denied(self):
        for record in self:
            record.state = "denied"

    def name_get(self):
        name = []
        for record in self:
            name.append((
                record.id, record.agreement_name
            ))
        return name

    @api.model
    def create(self, vals):
        if vals.get('agreement_seq', 'New') == 'New':
            vals['agreement_seq'] = self.env['ir.sequence'].next_by_code(
                'library.agreement.sequence') or 'New'
        result = super(Agreement, self).create(vals)
        return result
