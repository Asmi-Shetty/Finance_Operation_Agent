from decimal import Decimal
from app.services.po_matching import match_invoice_to_po
from app.services.duplicate_detection import detect_duplicate
from app.services.policy_validation import validate_policies
from app.services.anomaly_detection import score_anomalies
from app.services.decision_engine import approval_route, decide

INVOICE={"vendor_name":"ABC Technologies Pvt Ltd","invoice_number":"INV-10245","invoice_date":"2026-09-20","po_number":"PO-45321","currency":"INR","total":"118000"}
PO={"vendor_name":"ABC Technologies","currency":"INR","amount":"120000","committed_amount":"0"}

def test_po_match():
    result=match_invoice_to_po(INVOICE,PO)
    assert result["matched"] is True and result["amount_difference"]=="2000.00"

def test_duplicate_detection():
    result=detect_duplicate(INVOICE,[{"id":"prior","vendor_name":"ABC Technologies Pvt Ltd","invoice_number":"INV-10245","total":"118000"}])
    assert result["duplicate"] and "VENDOR_INVOICE_NUMBER" in result["matches"][0]["signals"]

def test_policy_and_routing():
    result=validate_policies(INVOICE)
    assert result["policy_status"]=="APPROVAL_REQUIRED"
    assert approval_route(Decimal("118000"))==["DEPARTMENT_MANAGER","FINANCE"]

def test_high_risk_duplicate_is_exception():
    po=match_invoice_to_po(INVOICE,PO); duplicate={"duplicate":True,"matches":[]}
    anomaly=score_anomalies(INVOICE,po,duplicate,[])
    decision=decide(extraction_confidence=Decimal("0.99"),po_match=po,policy=validate_policies(INVOICE,True),duplicate=duplicate,anomaly=anomaly)
    assert anomaly["risk_level"]=="HIGH" and decision["status"]=="EXCEPTION"

