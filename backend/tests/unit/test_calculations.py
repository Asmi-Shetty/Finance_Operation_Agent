from datetime import date
from decimal import Decimal
from app.services.calculations import *

def test_financial_calculations_use_decimal():
    items=[{"quantity":"2","unit_price":"19.995"},{"quantity":"1","unit_price":"10"}]
    assert calculate_subtotal(items)==Decimal("49.99")
    assert calculate_tax(Decimal("100000"),Decimal("0.18"))==Decimal("18000.00")
    assert calculate_total(Decimal("100000"),Decimal("18000"))==Decimal("118000.00")
    assert calculate_payment_due_date(date(2026,9,20),30)==date(2026,10,20)

def test_variance_and_remaining_amount():
    assert calculate_variance(Decimal("118000"),Decimal("120000"))==(Decimal("-2000.00"),Decimal("-0.0167"))
    assert calculate_remaining_po_amount(Decimal("120000"),Decimal("2000"))==Decimal("118000.00")

