from datetime import date, datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from app.models.entities import InvoiceStatus, RiskLevel

class InvoiceSummary(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    id: UUID; invoice_number: str|None; invoice_date: date|None; due_date: date|None
    subtotal: Decimal|None; tax: Decimal|None; total: Decimal|None; currency: str|None
    status: InvoiceStatus; risk_level: RiskLevel; anomaly_score: Decimal; created_at: datetime

class InvoiceList(BaseModel):
    items: list[InvoiceSummary]; total: int; page: int; page_size: int

class UploadResponse(BaseModel):
    invoice_id: UUID; status: InvoiceStatus; file_name: str; document_hash: str; next_action: str="PROCESS"

class ApprovalRequest(BaseModel):
    comments: str|None=Field(default=None, max_length=2000)

class ActionResponse(BaseModel):
    invoice_id: UUID; status: InvoiceStatus; message: str

class DashboardResponse(BaseModel):
    total_invoices: int; pending_review: int; approved: int; exceptions: int; duplicate_alerts: int; high_risk: int; total_invoice_value: Decimal

