import re
from decimal import Decimal
from app.services.calculations import calculate_remaining_po_amount, calculate_variance

def normalize(value: str) -> str:
    suffixes={"limited","ltd","pvt","private","llc","inc","technologies"}
    words=re.sub(r"[^a-z0-9 ]"," ",value.lower()).split()
    return " ".join(x for x in words if x not in suffixes)

def match_invoice_to_po(invoice: dict, po: dict) -> dict:
    issues=[]
    vendor_match=normalize(invoice.get("vendor_name", "")) == normalize(po.get("vendor_name", ""))
    if not vendor_match: issues.append("VENDOR_MISMATCH")
    currency_match=invoice.get("currency") == po.get("currency")
    if not currency_match: issues.append("CURRENCY_MISMATCH")
    remaining=calculate_remaining_po_amount(Decimal(str(po["amount"])),Decimal(str(po.get("committed_amount",0))))
    invoice_total=Decimal(str(invoice["total"])); amount_ok=invoice_total <= remaining
    if not amount_ok: issues.append("INVOICE_EXCEEDS_PO_REMAINING")
    difference,_=calculate_variance(remaining,invoice_total)
    score=Decimal("1.0")-Decimal("0.35")*len(issues)
    return {"matched":not issues,"match_score":str(max(Decimal("0"),score)),"amount_difference":str(difference),"remaining_po_amount":str(remaining),"issues":issues}

