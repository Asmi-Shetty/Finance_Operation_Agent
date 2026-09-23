from decimal import Decimal

def score_anomalies(invoice: dict, po_match: dict, duplicate: dict, history: list[dict]) -> dict:
    score=Decimal("0"); reasons=[]
    if duplicate["duplicate"]: score+=Decimal("0.70"); reasons.append("Duplicate invoice pattern detected")
    if not po_match.get("matched",False): score+=Decimal("0.35"); reasons.append("Invoice does not fully match the purchase order")
    amounts=[Decimal(str(x["total"])) for x in history if x.get("total") is not None]
    if amounts:
        average=sum(amounts)/len(amounts); current=Decimal(str(invoice["total"]))
        if average and current > average*Decimal("1.4"):
            score+=Decimal("0.30"); reasons.append(f"Amount is {((current/average)-1)*100:.0f}% above vendor average")
    if invoice.get("new_vendor"): score+=Decimal("0.20"); reasons.append("Vendor has no established invoice history")
    score=min(score,Decimal("1")); level="HIGH" if score>=Decimal("0.70") else "MEDIUM" if score>=Decimal("0.35") else "LOW"
    return {"risk_level":level,"anomaly_score":str(score.quantize(Decimal("0.01"))),"reasons":reasons}

