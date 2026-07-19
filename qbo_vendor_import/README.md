# Huron Market QBO Vendor Import

This module converts normalized vendor invoice data into:

- a QuickBooks Online bill-import CSV;
- a landscape Excel review workbook;
- invoice-level reconciliation results.

## Current scope

Version 1 implements the accounting and reconciliation engine, including Heidelberg's bottle-only split-charge rule. Invoice PDF extraction is intentionally separated from accounting logic so that extracted data can be reviewed before posting.

## Run

```bash
python -m qbo_vendor_import.cli examples/heidelberg_2026_07_14.json --output output
```

Generated files:

- `output/qbo_bill_import.csv`
- `output/ap_review.xlsx`

## Validation rule

An invoice is not exported unless its calculated QBO total equals the stated vendor invoice total to the cent.

## Input model

Each invoice contains direct department amounts plus optional split charges. Split charges are allocated by eligible `BO` bottle counts only. Case (`CA`) quantities never receive split-charge allocation.
