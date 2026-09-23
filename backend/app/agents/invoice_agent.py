import re
from datetime import date
from decimal import Decimal

PATTERNS={
 "vendor_name":r"Vendor\s*:\s*([^\n]+)","invoice_number":r"Invoice(?:\s+Number|\s*#)?\s*:\s*([\w-]+)",
 "po_number":r"PO(?:\s+Number|\s*#)?\s*:\s*([\w-]+)","subtotal":r"Subtotal\s*:\s*[₹$]?\s*([\d,]+(?:\.\d+)?)",
 "tax":r"(?:GST|Tax)\s*:\s*[₹$]?\s*([\d,]+(?:\.\d+)?)","total":r"Total\s*:\s*[₹$]?\s*([\d,]+(?:\.\d+)?)",
}
def extract_invoice(text: str) -> dict:
    values={}; confidence={}
    for field,pattern in PATTERNS.items():
        match=re.search(pattern,text,re.I)
        values[field]=match.group(1).strip() if match else None; confidence[field]="0.96" if match else "0.00"
    for field in ("subtotal","tax","total"):
        if values[field] is not None: values[field]=Decimal(values[field].replace(",",""))
    currency="INR" if "₹" in text or re.search(r"\bINR\b",text,re.I) else "USD" if "$" in text else None
    values.update(currency=currency,line_items=[],payment_terms=None,invoice_date=None,due_date=None)
    confidence["currency"]="0.90" if currency else "0.00"
    present=[Decimal(x) for x in confidence.values()]; minimum=min(present) if present else Decimal("0")
    return {"data":values,"confidence":confidence,"minimum_confidence":str(minimum)}

