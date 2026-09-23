from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

MONEY = Decimal("0.01")

def money(value: Decimal | str | int) -> Decimal:
    return Decimal(str(value)).quantize(MONEY, rounding=ROUND_HALF_UP)

def calculate_subtotal(items: list[dict]) -> Decimal:
    return money(sum((Decimal(str(x["quantity"])) * Decimal(str(x["unit_price"])) for x in items), Decimal("0")))

def calculate_tax(subtotal: Decimal, tax_rate: Decimal) -> Decimal:
    if tax_rate < 0: raise ValueError("Tax rate cannot be negative")
    return money(subtotal * tax_rate)

def calculate_total(subtotal: Decimal, tax: Decimal) -> Decimal:
    return money(subtotal + tax)

def calculate_variance(invoice_total: Decimal, reference_total: Decimal) -> tuple[Decimal, Decimal]:
    absolute = money(invoice_total - reference_total)
    percentage = Decimal("0") if reference_total == 0 else (absolute / reference_total).quantize(Decimal("0.0001"))
    return absolute, percentage

def calculate_remaining_po_amount(po_amount: Decimal, committed_amount: Decimal) -> Decimal:
    return money(max(Decimal("0"), po_amount - committed_amount))

def calculate_payment_due_date(invoice_date: date, terms_days: int) -> date:
    if terms_days < 0: raise ValueError("Payment terms cannot be negative")
    return invoice_date + timedelta(days=terms_days)

