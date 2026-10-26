# -*- coding: utf-8 -*-
{
    'name': 'DG Erzberger Custom',
    'version': '19.0.1.5.0',
    'summary': 'Client-specific changes on top of the vendored Erzberger modules',
    'description': """
Erzberger Verpackungssysteme / Erzberger Holzkunst - client changes
===================================================================

This module holds *our* changes for the Erzberger instance.  The vendored
upstream modules (``erzberger_customizations``, ``erzberger_sale_report``,
``erzberger_import_automations``, ``erzberger_pos_epson_tse``) are kept
untouched so that an upstream update stays a clean, readable diff against
the frozen ``vendor/erzberger-addons`` branch.

Content:

* ``sale.order.customer_contact_name`` - manually fillable "who ordered at
  the customer" field, printed on the Auftragsbestätigung instead of the
  Erzberger employee (``user_id``).
* ``purchase.order.sale_order_id`` - link a purchase order to an existing
  sales order, pre-filled from the source document.
* Payment term fallback from the vendor's commercial partner, so the
  vendor's agreed terms actually land on the purchase order.
* Auftragsbestätigung adjustments: website without ``http://``, delivery
  date as calendar week (KW), hide the reference line when empty.
* Holzkunst letterhead: company logo no longer forced to a fixed
  width/height ratio (was printed squashed).
* Purchase order report: "Payment Terms" label hidden when no term is set.
* Purchase order report re-styled to the invoice format (same letterhead,
  same body layout) instead of the standard Odoo purchase layout.
* Rechnung: the Factur-X/ZUGFeRD hybrid PDF is built from the Erzberger
  invoice layout instead of the standard Odoo report (journal default +
  account.custom_templates_facturx_list).
* Rechnung: po_number compute fixed for Odoo 19 (the vendored one uses the
  removed sale.order.procurement_group_id and broke printing of new invoices).
* Rechnung: the quotation text (Terms and conditions, also the text coming
  from the quotation template) is no longer copied into the invoice.
* Lieferschein: "Kundenreferenz" (customer's order number), taken from the
  sales order, shown on the picking and printed on the delivery note.
* Shared letterhead footer: spaced slash ("Zwönitz / Erzgebirge") and the
  country line no longer prints "Deutschland/Deutschland".

See ``README.md`` for the to-do mapping and the items that are data /
configuration work on the live instance.
""",
    'category': 'Sales',
    'author': 'Passform Digital',
    'license': 'LGPL-3',
    'depends': [
        'sale',
        'purchase',
        'l10n_de',
        'erzberger_sale_report',
        'erzberger_customizations',
        'sale_stock',
    ],
    'data': [
        'views/sale_order_views.xml',
        'views/purchase_order_views.xml',
        'views/stock_picking_views.xml',
        'report/auftragsbestaetigung_patch.xml',
        'report/holzkunst_layout_patch.xml',
        'report/purchase_order_patch.xml',
        'report/layout_footer_patch.xml',
        'report/purchase_order_report.xml',
        'report/delivery_slip_customer_ref.xml',
        'data/ir_config_parameter.xml',
    ],
    'post_init_hook': 'hooks.set_journal_invoice_templates',
    'installable': True,
    'application': False,
    'auto_install': False,
}
