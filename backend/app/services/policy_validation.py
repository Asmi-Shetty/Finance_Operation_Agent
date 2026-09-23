from decimal import Decimal

POLICIES = [
    {"id":"approval-manager","rule":"Invoices at or above ₹100,000 require manager and finance approval","source":"approval_policy.md"},
    {"id":"approval-head","rule":"Invoices above ₹500,000 require finance-head approval","source":"approval_policy.md"},
    {"id":"missing-po","rule":"Invoices with missing PO numbers require manual review","source":"invoice_policy.md"},
    {"id":"duplicate","rule":"Duplicate invoices must never be automatically approved","source":"invoice_policy.md"},
]

def retrieve_policies(invoice: dict) -> list[dict]:
    terms={"invoice","approval"}
    if not invoice.get("po_number"): terms.add("po")
    return [p for p in POLICIES if any(t in p["rule"].lower() for t in terms)]

def validate_policies(invoice: dict, duplicate: bool=False) -> dict:
    total=Decimal(str(invoice.get("total",0))); triggered=[]
    if total > Decimal("500000"): triggered.append({**POLICIES[1],"evidence":f"invoice total = {total}"})
    elif total >= Decimal("100000"): triggered.append({**POLICIES[0],"evidence":f"invoice total = {total}"})
    if not invoice.get("po_number"): triggered.append({**POLICIES[2],"evidence":"PO number is missing"})
    if duplicate: triggered.append({**POLICIES[3],"evidence":"deterministic duplicate signals found"})
    exception=any(x["id"] in {"missing-po","duplicate"} for x in triggered)
    return {"policy_status":"EXCEPTION" if exception else ("APPROVAL_REQUIRED" if triggered else "PASS"),"rules_triggered":triggered,"sources":sorted({x["source"] for x in triggered})}

