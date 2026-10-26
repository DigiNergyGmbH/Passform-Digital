# -*- coding: utf-8 -*-
from odoo.addons.dg_erzberger_custom.hooks import set_journal_invoice_templates


def migrate(cr, version):
    from odoo import api, SUPERUSER_ID
    env = api.Environment(cr, SUPERUSER_ID, {})
    set_journal_invoice_templates(env)
