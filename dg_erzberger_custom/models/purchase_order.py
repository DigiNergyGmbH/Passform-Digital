# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    sale_order_id = fields.Many2one(
        'sale.order',
        string='Verkaufsauftrag',
        help="Verknüpfter Verkaufsauftrag. Wird beim Anlegen automatisch aus dem "
             "Quellbeleg (origin) ermittelt und kann jederzeit manuell geändert "
             "oder gesetzt werden.",
        copy=False,
    )
    sale_order_name = fields.Char(
        string='Verkaufsauftrags-Nr.',
        related='sale_order_id.name',
        store=True,
    )
    customer_contact_name = fields.Char(
        string='Besteller (Kunde)',
        related='sale_order_id.customer_contact_name',
    )

    @api.onchange('sale_order_id')
    def _onchange_sale_order_id(self):
        for order in self:
            if order.sale_order_id and not order.origin:
                order.origin = order.sale_order_id.name

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        for order in orders:
            # 1) link the originating sales order
            if not order.sale_order_id and order.origin:
                names = [n.strip() for n in order.origin.split(',') if n.strip()]
                if names:
                    order.sale_order_id = self.env['sale.order'].search(
                        [('name', 'in', names)], limit=1
                    )
            # 2) vendor payment terms: fall back to the commercial partner
            #    (Odoo only reads the property from the exact contact, so a term
            #    stored on the vendor company is silently ignored)
            if not order.payment_term_id:
                partner = order.partner_id.commercial_partner_id
                term = partner.property_supplier_payment_term_id
                if term:
                    order.payment_term_id = term
        return orders
