from decimal import Decimal
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.models.entities import Invoice, InvoiceStatus, RiskLevel
from app.schemas.invoice import DashboardResponse
router=APIRouter()

@router.get("",response_model=DashboardResponse)
async def dashboard(session: AsyncSession=Depends(get_session)):
    statuses=dict((await session.execute(select(Invoice.status,func.count()).group_by(Invoice.status))).all())
    total=await session.scalar(select(func.coalesce(func.sum(Invoice.total),0)))
    high=await session.scalar(select(func.count()).select_from(Invoice).where(Invoice.risk_level==RiskLevel.HIGH))
    return DashboardResponse(total_invoices=sum(statuses.values()),pending_review=statuses.get(InvoiceStatus.PENDING_APPROVAL,0),approved=statuses.get(InvoiceStatus.PAYMENT_READY,0)+statuses.get(InvoiceStatus.APPROVED,0),exceptions=statuses.get(InvoiceStatus.EXCEPTION,0),duplicate_alerts=0,high_risk=high or 0,total_invoice_value=Decimal(str(total or 0)))

