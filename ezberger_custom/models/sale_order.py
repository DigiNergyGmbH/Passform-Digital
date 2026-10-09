# -*- coding: utf-8 -*-
from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    customer_contact_name = fields.Char(
        string='Besteller (Kunde)',
        help="Name der Person beim Kunden, die den Auftrag erteilt hat.\n"
             "Erscheint auf der Auftragsbestätigung in der Zeile "
             "'(Ihr Auftrag v. ... p. Email v. ...)'. Ist das Feld leer, wird "
             "die Zeile nicht gedruckt.",
        copy=True,
    )
