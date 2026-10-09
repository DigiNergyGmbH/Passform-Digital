# -*- coding: utf-8 -*-
{
    'name': 'Erzberger Client Customizations',
    'version': '19.0.1.0.0',
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
    ],
    'data': [
        'views/sale_order_views.xml',
        'views/purchase_order_views.xml',
        'report/auftragsbestaetigung_patch.xml',
        'report/holzkunst_layout_patch.xml',
        'report/purchase_order_patch.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
