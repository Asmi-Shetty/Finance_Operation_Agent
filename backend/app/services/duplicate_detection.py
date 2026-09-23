from hashlib import sha256

def normalized_key(value: str | None) -> str:
    return "".join((value or "").lower().split())

def detect_duplicate(candidate: dict, existing: list[dict]) -> dict:
    matches=[]
    for prior in existing:
        signals=[]
        if candidate.get("document_hash") and candidate["document_hash"]==prior.get("document_hash"): signals.append("DOCUMENT_HASH")
        same_vendor=normalized_key(candidate.get("vendor_name"))==normalized_key(prior.get("vendor_name"))
        if same_vendor and normalized_key(candidate.get("invoice_number"))==normalized_key(prior.get("invoice_number")): signals.append("VENDOR_INVOICE_NUMBER")
        if same_vendor and candidate.get("invoice_date")==prior.get("invoice_date") and candidate.get("total")==prior.get("total"): signals.append("VENDOR_DATE_AMOUNT")
        if candidate.get("po_number") and candidate.get("po_number")==prior.get("po_number") and candidate.get("total")==prior.get("total"): signals.append("PO_AMOUNT")
        if signals: matches.append({"invoice_id":prior.get("id"),"signals":signals})
    return {"duplicate":bool(matches),"matches":matches}

