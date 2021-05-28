import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
import re
import logging


# logging.info("afasffas")


class Agreement(models.Model):
    _name = "library.agreement"
    _description = "Agreement"
    _inherit = 'mail.thread'

    _sql_constraints = [
        ('unique_agreement',
         'unique(library_ids, '
         'librarian_ids)',
         'The Agreement you are '
         'trying to create already exists.')]

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

    agreement_date = fields.Date(
        'Created Date',
        required=True,
        default=fields.Date.today()
    )

    agreement_date_deadline = fields.Date(
        default=lambda record: fields.Date.today() + relativedelta(days=30))

    library_ids = fields.Many2one(
        'library.library',
        required=True,
        domain=[('state', 'in', ('public', 'private'))],
        string='Libraries')

    librarian_ids = fields.Many2one(
        'library.librarian',
        required=True,
        string='Librarians')

    user_id = fields.Many2one('res.users')

    agreement_file = fields.Many2many(
        'ir.attachment',
        'class_ir_attachments_rel',
        'class_id',
        'attachment_id',
        string="Agreement files",
        required=True)

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

    @api.constrains('agreement_file')
    def _check_attachment(self):
        for record in self:
            if not record.agreement_file:
                raise ValidationError(
                    "You need to enter at least"
                    " one attachment to proceed."
                )

    @api.model
    def process_scheduler_queue(self):
        for rec in self.env["library.agreement"].search([('state', '!=', 'denied')]):
            if rec.agreement_date_deadline and rec.agreement_date_deadline == fields.Date.today():
                rec.write({'state': 'denied'})

    def action_send_card(self):
        template_id = self.env.ref('library.agreement_email_template').id
        data_id = self.env['ir.attachment'].browse(self.agreement_file.ids)
        template = self.env['mail.template'].browse(template_id)
        for existing_pdf in template.attachment_ids:
            template.write({"attachment_ids": [(3, existing_pdf.id)]})
        for pdf in data_id:
            for new_pdf in pdf:
                template.write({"attachment_ids": [(4, new_pdf.id)]})
        template.send_mail(self.id, force_send=True)
