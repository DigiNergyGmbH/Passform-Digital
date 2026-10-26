# -*- coding: utf-8 -*-
"""Sale journals print the Erzberger invoice template, not the Odoo default.

account.move.send picks the PDF template from
journal.invoice_template_pdf_report_id and falls back to the standard
account.account_invoices report.  With the fallback, every automatically
generated invoice PDF (and therefore the Factur-X/ZUGFeRD hybrid PDF the
customer receives) used the plain Odoo layout.

The journals are per database, so they are set in a migration rather than in
a data file.
"""


def set_journal_invoice_templates(env):
    # the parameter may already exist (it was often set by hand); set it
    # instead of inserting a data record, which would collide on the key
    env['ir.config_parameter'].sudo().set_param(
        'account.custom_templates_facturx_list',
        'erzberger_sale_report.report_invoice_document_custom,'
        'erzberger_sale_report.report_invoice_document_custom_holzenberg',
    )

    journals = env['account.journal'].search([('type', '=', 'sale')])
    for journal in journals:
        if journal.company_id.name and 'Holzkunst' in journal.company_id.name:
            report_name = 'erzberger_sale_report.report_invoice_document_custom_holzenberg'
        else:
            report_name = 'erzberger_sale_report.report_invoice_document_custom'

        report = env['ir.actions.report'].search([('report_name', '=', report_name)], limit=1)
        if not report:
            continue
        if journal.invoice_template_pdf_report_id != report:
            journal.invoice_template_pdf_report_id = report.id
            print('dg_erzberger_custom: journal %s -> %s' % (journal.name, report_name))
