from decimal import Decimal

def decide(*, extraction_confidence: Decimal, po_match: dict, policy: dict, duplicate: dict, anomaly: dict, threshold: Decimal=Decimal("0.85")) -> dict:
    if duplicate["duplicate"]: return {"status":"EXCEPTION","reason":"DUPLICATE_REVIEW_REQUIRED"}
    if extraction_confidence < threshold: return {"status":"EXCEPTION","reason":"LOW_EXTRACTION_CONFIDENCE"}
    if not po_match["matched"]: return {"status":"EXCEPTION","reason":"PO_MATCH_FAILED"}
    if anomaly["risk_level"]=="HIGH": return {"status":"EXCEPTION","reason":"HIGH_ANOMALY_RISK"}
    return {"status":"PENDING_APPROVAL","reason":"HUMAN_APPROVAL_REQUIRED"}

def approval_route(total: Decimal) -> list[str]:
    if total > Decimal("500000"): return ["FINANCE_HEAD"]
    if total >= Decimal("100000"): return ["DEPARTMENT_MANAGER","FINANCE"]
    return ["DEPARTMENT_MANAGER"]

