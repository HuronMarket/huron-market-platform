from __future__ import annotations

import csv
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Iterable

QBO_COLUMNS = [
    "VendorName",
    "RefNumber",
    "BillDate",
    "DueDate",
    "Terms",
    "Account",
    "LineAmount",
    "Memo",
]

MONEY = Decimal("0.01")


@dataclass(frozen=True)
class BillLine:
    account: str
    amount: Decimal
    memo: str


@dataclass(frozen=True)
class Bill:
    vendor_name: str
    ref_number: str
    bill_date: str
    due_date: str
    terms: str
    invoice_total: Decimal
    lines: tuple[BillLine, ...]

    @property
    def qbo_total(self) -> Decimal:
        return sum((line.amount for line in self.lines), Decimal("0.00"))

    @property
    def difference(self) -> Decimal:
        return (self.qbo_total - self.invoice_total).quantize(MONEY)

    def validate(self) -> None:
        if self.difference != Decimal("0.00"):
            raise ValueError(
                f"Invoice {self.ref_number} does not balance: "
                f"QBO={self.qbo_total} Invoice={self.invoice_total} "
                f"Difference={self.difference}"
            )
        if not self.lines:
            raise ValueError(f"Invoice {self.ref_number} has no bill lines")
        for line in self.lines:
            if line.amount == Decimal("0.00"):
                raise ValueError(
                    f"Invoice {self.ref_number} contains a zero-dollar line"
                )


def money(value: str | int | float | Decimal) -> Decimal:
    return Decimal(str(value)).quantize(MONEY, rounding=ROUND_HALF_UP)


def write_qbo_csv(bills: Iterable[Bill], output_path: Path) -> None:
    bill_list = list(bills)
    for bill in bill_list:
        bill.validate()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=QBO_COLUMNS)
        writer.writeheader()
        for bill_index, bill in enumerate(bill_list):
            if bill_index:
                writer.writerow({column: "" for column in QBO_COLUMNS})
            for line in bill.lines:
                writer.writerow(
                    {
                        "VendorName": bill.vendor_name,
                        "RefNumber": bill.ref_number,
                        "BillDate": bill.bill_date,
                        "DueDate": bill.due_date,
                        "Terms": bill.terms,
                        "Account": line.account,
                        "LineAmount": f"{line.amount:.2f}",
                        "Memo": line.memo,
                    }
                )
