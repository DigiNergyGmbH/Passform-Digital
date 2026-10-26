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

    def _prepare_invoice(self):
        """Do not carry the quotation text into the invoice.

        The terms and conditions of a quotation (including the text that comes
        from the quotation template) are copied to the invoice narration by
        Odoo (sale/models/sale_order.py: 'narration': self.note).  The customer
        wants that text on the quotation only, so the narration stays empty
        unless it is typed on the invoice itself.
        """
        vals = super()._prepare_invoice()
        vals.pop('narration', None)
        return vals
