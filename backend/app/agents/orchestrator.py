from typing import TypedDict
from langgraph.graph import END, START, StateGraph
from app.services.anomaly_detection import score_anomalies
from app.services.decision_engine import decide
from app.services.duplicate_detection import detect_duplicate
from app.services.policy_validation import validate_policies
from app.services.po_matching import match_invoice_to_po

class FinanceState(TypedDict, total=False):
    invoice_id: str; extracted_invoice: dict; extraction_confidence: str; po_data: dict
    po_match_result: dict; policy_results: dict; duplicate_result: dict; anomaly_result: dict
    validation_result: dict; approval_required: bool; approval_status: str; final_status: str
    history: list[dict]; existing_invoices: list[dict]; audit_events: list[dict]

def po_node(s): return {"po_match_result":match_invoice_to_po(s["extracted_invoice"],s["po_data"])}
def duplicate_node(s): return {"duplicate_result":detect_duplicate(s["extracted_invoice"],s.get("existing_invoices",[]))}
def policy_node(s): return {"policy_results":validate_policies(s["extracted_invoice"],s["duplicate_result"]["duplicate"])}
def anomaly_node(s): return {"anomaly_result":score_anomalies(s["extracted_invoice"],s["po_match_result"],s["duplicate_result"],s.get("history",[]))}
def decision_node(s):
    result=decide(extraction_confidence=s["extraction_confidence"],po_match=s["po_match_result"],policy=s["policy_results"],duplicate=s["duplicate_result"],anomaly=s["anomaly_result"])
    return {"final_status":result["status"],"approval_required":result["status"]=="PENDING_APPROVAL","validation_result":result}

def build_graph():
    graph=StateGraph(FinanceState)
    for name,node in [("match_po",po_node),("duplicates",duplicate_node),("policy",policy_node),("anomaly",anomaly_node),("decision",decision_node)]: graph.add_node(name,node)
    graph.add_edge(START,"match_po"); graph.add_edge("match_po","duplicates"); graph.add_edge("duplicates","policy"); graph.add_edge("policy","anomaly"); graph.add_edge("anomaly","decision"); graph.add_edge("decision",END)
    return graph.compile()

finance_graph=build_graph()

