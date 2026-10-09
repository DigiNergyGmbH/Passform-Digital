# dg_erzberger_custom

Client-specific changes for the **Erzberger Verpackungssysteme / Erzberger Holzkunst**
instance. The vendored upstream modules stay untouched; this module only inherits
from them, so an upstream update remains a readable diff against the frozen
`vendor/erzberger-addons` branch.

```
depends = sale, purchase, l10n_de, erzberger_sale_report, erzberger_customizations
```

---

## Source: the customer's to-do list

`TO DO_ Erzberger_Verpackungssysteme_.pdf`, page 1, verbatim:

```
Erzberger/Verpackungssysteme:

1. TSE Einheit verbinden
   Kunde hat Bondrucker Epson TM-m30III + Epson USB Stick für TSE

2. Footer falsche UST-ID: VAT: DE141313958

3. Bitte prüfen ob diese Infos an der Firma hinterlegt sind
   VAT: DE141313958
   St.-Nr.: 224/241/02257
   W-IdNr.: DE141313958-00001

4. obwohl eine Zahlungsbedingung (15 Tage) beim Hersteller hinterlegt ist,
   wird diese nicht in die Bestellung gezogen (den Eintrag 14 Tage habe ich
   über die Bedingungen händisch gemacht - bzw. müssten wir die 14 Tage
   noch anlegen, da nur 15 Tage zur Auswahl steht)

5. Auftragsbestätigung: siehe screenshot
```

Annotations found in the PDF attachments (page 2 of the to-do PDF, plus the
`Angebot *.pdf` files):

| Document | Annotation | Refers to |
|---|---|---|
| Auftragsbestätigung (to-do p. 2) | "*The employee of Erzberger should not be in it here, you would like to be able to enter the person who ordered from you by e-mail. So need a field in odoo that you can fill in manually!*" + wavy line | `(Ihr Auftrag v. 05.10.2026 p. Email v. Anett Kretzschmar)` |
| Angebot - S00040-2, p. 1 | Square on the quantity value + `Einheit` | quantity column |
| Angebot - S00040-2, p. 1 | Square on `Website: http://www.erzberger-verpackungssysteme.de` + `http://` | footer/letterhead website |
| Angebot - S00040-2, p. 1 | Square on `Preis/Einheit per kg/1.000 Stück` + `kg / 1.000 Stück / Stück` | price column header |
| Angebot - S00041-2, p. 1 | `Logo gestaucht` | Holzkunst letterhead logo |
| Angebot - S00041-2, p. 1 | `Falsche Farbe` | Holzkunst letterhead logo |
| Bestellung - P00044.pdf | (no annotation) printed as-is | empty `Zahlungsbedingungen:` line |

---

## Status

### Implemented in this module

| # | Item | Where |
|---|---|---|
| 5 | New field `sale.order.customer_contact_name` ("Besteller (Kunde)"), editable in the sale order form, pre-filled from the customer contact. Printed on the AB instead of the Erzberger employee; the line disappears when the field is empty. | `models/sale_order.py`, `views/sale_order_views.xml`, `report/auftragsbestaetigung_patch.xml` |
| 5 | Column sub-headers: `kg/Stück` → `Einheit`, `per kg/1.000 Stück` → `kg / 1.000 Stück / Stück`; the line's unit of measure is printed next to the quantity. | `report/auftragsbestaetigung_patch.xml` |
| 5 | Delivery date printed as calendar week under `Datum:` (`Liefertermin: KW nn`, from `commitment_date`, ISO week). | `report/auftragsbestaetigung_patch.xml` |
| 5 | Website printed without the protocol (`www.erzberger-verpackungssysteme.de` instead of `http://…`) on the Verpackungssysteme letterhead. | `report/holzkunst_layout_patch.xml` |
| – | Holzkunst letterhead logo: the fixed `width:42mm; height:48mm` squashed the logo; height is now automatic, aspect ratio kept. Applies to Angebot/AB, invoice and delivery note (they share `report_erz_external_layouts_holzkenber`). | `report/holzkunst_layout_patch.xml` |
| 4 | `purchase.order.sale_order_id` – link a purchase order to an existing sales order (auto-filled from the source document `origin`, freely editable) plus `sale_order_name` in the purchase list. | `models/purchase_order.py`, `views/purchase_order_views.xml` |
| 4 | Payment term fallback on purchase orders: when the order has no term, the *commercial partner's* supplier payment term is applied (Odoo itself only reads the property from the exact contact, which is why a term stored on the vendor company is silently ignored). | `models/purchase_order.py` |
| 4 | Purchase order PDF no longer prints an empty `Zahlungsbedingungen:` / `Payment Terms:` label when no term is set. | `report/purchase_order_patch.xml` |

Every inherited view was checked against the real arch files: all eight xpath
expressions match exactly one node, all three inherit targets exist
(`sale.view_order_form`, `purchase.purchase_order_form`,
`purchase.purchase_order_view_tree`). Note: `external_layout_din5008_custom` in
`delivery_slip_template.xml` is **commented out** upstream – do not inherit it.

### Still to do – data / configuration on the live instance

| # | Item | Action |
|---|---|---|
| 1 | TSE | `erzberger_pos_epson_tse` is installed; the POS payment method still needs the Epson TM-m30III + the Epson USB stick (TSE) configured – serial, IP/port and the TSE number come from the device. Needs access to the POS and the hardware. |
| 2 | Footer USt-IdNr. | Set the correct VAT on the company (`res.company.vat`). The printed AB currently shows the demo value `DE123456788`; the correct value is `DE141313958`. Company must be `Erzberger Verpackungssysteme`. |
| 3 | Company data | Check/fill in Settings → Companies (visible for country = Germany): `vat` = `DE141313958`, `l10n_de_stnr` (St.-Nr.) = `224/241/02257`, `l10n_de_widnr` (W-IdNr.) = `DE141313958-00001`. The AB currently prints St.-Nr. and USt-IdNr. only – the W-IdNr. is *not* printed anywhere; say the word if it should appear on the AB. The footer of `Bestellung - P00044.pdf` also shows an empty `HRB-Nr.:` – that is the company's register number field. |
| 4 | Payment terms | Create the missing payment term **14 Tage netto** (only `15 Tage` exists today), and store `15 Tage` as **supplier** payment term on the vendor `JG-Verpackungen GmbH` – including the parent company contact, otherwise the fallback in the code is what saves it. |
| – | `Logo gestaucht` / `Falsche Farbe` | The squash is fixed in code. "Falsche Farbe" is the logo *file*: the company logo on `Erzberger Holzkunst` is a wrong-colour version. A correct logo (vector) has to be supplied and set as the company logo – the two PDFs in the mail (`Logo Erzberger 2023.pdf`, `EE-Logo_VEKS_Vektor.pdf`) are the candidates. |
| – | Auftragsbestätigung "siehe screenshot" | Implemented. The `Bearbeiter:` row was intentionally left as is – that field means the Erzberger employee handling the order, which is correct; only the "(Ihr Auftrag v. … p. Email v. …)" line was wrong. |

### Open questions

* Optional positions (`display_type`) are still listed as empty rows and still count
  into nothing – the customer mentioned this in a mail; the exact expectation is
  unclear (hide them entirely / print them but keep them out of the totals).
* "Steuer Einkauf auf Netto umstellen" – the purchase order PDF already prints net
  prices plus VAT; needs a concrete example of what is wrong.
* A dedicated letterhead for the purchase order ("Briefkopf Einkauf") is not built
  yet; the printed PO comes from the standard Odoo report with the standard Odoo
  letterhead.
