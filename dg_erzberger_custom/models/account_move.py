# -*- coding: utf-8 -*-
from odoo import api, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    # erzberger_sale_report computes po_number with
    # sale.order.procurement_group_id, a field that no longer exists in Odoo 19
    # (procurement groups were removed).  Any invoice whose lines come from a
    # sale order *without* a linked purchase order therefore raised
    # KeyError: 'procurement_group_id' when the field was computed - which
    # happens right after the invoice is created, so the PDF could not be
    # printed.  The whole compute method is replaced; it only uses fields that
    # exist in 19.0.
    @api.depends('invoice_line_ids', 'invoice_origin')
    def _compute_po_number(self):
        PurchaseOrder = self.env['purchase.order']
        for move in self:
            sale_orders = move.invoice_line_ids.sale_line_ids.order_id
            if not sale_orders and move.invoice_origin:
                sale_orders = self.env['sale.order'].search(
                    [('name', '=', move.invoice_origin)], limit=1)

            orders = PurchaseOrder
            if sale_orders:
                orders = PurchaseOrder.search(
                    [('origin', 'in', sale_orders.mapped('name'))])
            if not orders and sale_orders:
                # explicit link maintained by this module (purchase.order.sale_order_id)
                orders = PurchaseOrder.search(
                    [('sale_order_id', 'in', sale_orders.ids)])
            if not orders and sale_orders:
                orders = sale_orders.order_line.purchase_line_ids.order_id

            move.po_number = ", ".join(orders.mapped('name')) if orders else False
