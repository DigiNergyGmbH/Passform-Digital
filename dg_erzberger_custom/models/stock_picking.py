# -*- coding: utf-8 -*-
from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    customer_order_ref = fields.Char(
        string='Kundenreferenz',
        compute='_compute_customer_order_ref',
        store=True,
        readonly=False,
        copy=False,
        help="Bestellnummer des Kunden. Wird aus dem Verkaufsauftrag übernommen, "
             "kann hier korrigiert werden und erscheint auf dem Lieferschein.",
    )

    @api.depends('sale_id.client_order_ref',
                 'move_ids.sale_line_id.order_id.client_order_ref')
    def _compute_customer_order_ref(self):
        for picking in self:
            # keep a value that was typed on the picking
            if picking.customer_order_ref:
                continue
            sale = picking.sale_id or picking.move_ids.sale_line_id.order_id[:1]
            picking.customer_order_ref = sale.client_order_ref or False
