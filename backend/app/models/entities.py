import enum
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from sqlalchemy import Date, DateTime, Enum, ForeignKey, JSON, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin

class InvoiceStatus(str, enum.Enum):
    UPLOADED="UPLOADED"; PROCESSING="PROCESSING"; VALIDATED="VALIDATED"; EXCEPTION="EXCEPTION"
    PENDING_APPROVAL="PENDING_APPROVAL"; APPROVED="APPROVED"; REJECTED="REJECTED"
    CLARIFICATION_REQUESTED="CLARIFICATION_REQUESTED"; PAYMENT_READY="PAYMENT_READY"; PAID="PAID"

class RiskLevel(str, enum.Enum):
    LOW="LOW"; MEDIUM="MEDIUM"; HIGH="HIGH"

class ApprovalStatus(str, enum.Enum):
    PENDING="PENDING"; APPROVED="APPROVED"; REJECTED="REJECTED"; CLARIFICATION_REQUESTED="CLARIFICATION_REQUESTED"

class User(Base, TimestampMixin):
    __tablename__="users"
    id: Mapped[uuid.UUID]=mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str]=mapped_column(String(200)); email: Mapped[str]=mapped_column(String(320), unique=True, index=True)
    department: Mapped[str]=mapped_column(String(120)); role: Mapped[str]=mapped_column(String(80))
    manager_id: Mapped[uuid.UUID|None]=mapped_column(ForeignKey("users.id"), nullable=True)

class Vendor(Base, TimestampMixin):
    __tablename__="vendors"
    id: Mapped[uuid.UUID]=mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str]=mapped_column(String(240)); normalized_name: Mapped[str]=mapped_column(String(240), index=True)
    tax_id: Mapped[str|None]=mapped_column(String(100), nullable=True); address: Mapped[str|None]=mapped_column(Text, nullable=True)
    status: Mapped[str]=mapped_column(String(40), default="ACTIVE"); risk_level: Mapped[RiskLevel]=mapped_column(Enum(RiskLevel), default=RiskLevel.LOW)

class PurchaseOrder(Base, TimestampMixin):
    __tablename__="purchase_orders"
    id: Mapped[uuid.UUID]=mapped_column(primary_key=True, default=uuid.uuid4)
    po_number: Mapped[str]=mapped_column(String(100), unique=True, index=True); vendor_id: Mapped[uuid.UUID]=mapped_column(ForeignKey("vendors.id"))
    department: Mapped[str]=mapped_column(String(120)); amount: Mapped[Decimal]=mapped_column(Numeric(18,2)); committed_amount: Mapped[Decimal]=mapped_column(Numeric(18,2), default=Decimal("0"))
    currency: Mapped[str]=mapped_column(String(3)); status: Mapped[str]=mapped_column(String(40), default="OPEN")
    vendor: Mapped[Vendor]=relationship(); items: Mapped[list["PurchaseOrderItem"]]=relationship(cascade="all, delete-orphan")

class PurchaseOrderItem(Base):
    __tablename__="purchase_order_items"
    id: Mapped[uuid.UUID]=mapped_column(primary_key=True, default=uuid.uuid4); po_id: Mapped[uuid.UUID]=mapped_column(ForeignKey("purchase_orders.id"))
    description: Mapped[str]=mapped_column(String(500)); quantity: Mapped[Decimal]=mapped_column(Numeric(18,4)); unit_price: Mapped[Decimal]=mapped_column(Numeric(18,2)); total: Mapped[Decimal]=mapped_column(Numeric(18,2))

class Invoice(Base, TimestampMixin):
    __tablename__="invoices"; __table_args__=(UniqueConstraint("vendor_id", "invoice_number", name="uq_vendor_invoice_number"),)
    id: Mapped[uuid.UUID]=mapped_column(primary_key=True, default=uuid.uuid4); invoice_number: Mapped[str|None]=mapped_column(String(100), nullable=True, index=True)
    vendor_id: Mapped[uuid.UUID|None]=mapped_column(ForeignKey("vendors.id"), nullable=True); po_id: Mapped[uuid.UUID|None]=mapped_column(ForeignKey("purchase_orders.id"), nullable=True)
    invoice_date: Mapped[date|None]=mapped_column(Date, nullable=True); due_date: Mapped[date|None]=mapped_column(Date, nullable=True)
    subtotal: Mapped[Decimal|None]=mapped_column(Numeric(18,2), nullable=True); tax: Mapped[Decimal|None]=mapped_column(Numeric(18,2), nullable=True); total: Mapped[Decimal|None]=mapped_column(Numeric(18,2), nullable=True)
    currency: Mapped[str|None]=mapped_column(String(3), nullable=True); status: Mapped[InvoiceStatus]=mapped_column(Enum(InvoiceStatus), default=InvoiceStatus.UPLOADED, index=True)
    risk_level: Mapped[RiskLevel]=mapped_column(Enum(RiskLevel), default=RiskLevel.LOW); anomaly_score: Mapped[Decimal]=mapped_column(Numeric(5,4), default=Decimal("0")); version: Mapped[int]=mapped_column(default=1)
    vendor: Mapped[Vendor|None]=relationship(); po: Mapped[PurchaseOrder|None]=relationship(); items: Mapped[list["InvoiceItem"]]=relationship(cascade="all, delete-orphan")
    documents: Mapped[list["InvoiceDocument"]]=relationship(cascade="all, delete-orphan")

class InvoiceItem(Base):
    __tablename__="invoice_items"
    id: Mapped[uuid.UUID]=mapped_column(primary_key=True, default=uuid.uuid4); invoice_id: Mapped[uuid.UUID]=mapped_column(ForeignKey("invoices.id"))
    description: Mapped[str]=mapped_column(String(500)); quantity: Mapped[Decimal]=mapped_column(Numeric(18,4)); unit_price: Mapped[Decimal]=mapped_column(Numeric(18,2)); total: Mapped[Decimal]=mapped_column(Numeric(18,2))

class InvoiceDocument(Base):
    __tablename__="invoice_documents"
    id: Mapped[uuid.UUID]=mapped_column(primary_key=True, default=uuid.uuid4); invoice_id: Mapped[uuid.UUID]=mapped_column(ForeignKey("invoices.id"), index=True)
    file_name: Mapped[str]=mapped_column(String(255)); storage_key: Mapped[str]=mapped_column(String(500)); media_type: Mapped[str]=mapped_column(String(100)); document_hash: Mapped[str]=mapped_column(String(64), index=True)

class Policy(Base, TimestampMixin):
    __tablename__="policies"
    id: Mapped[uuid.UUID]=mapped_column(primary_key=True, default=uuid.uuid4); title: Mapped[str]=mapped_column(String(240)); source_name: Mapped[str]=mapped_column(String(240))
    content: Mapped[str]=mapped_column(Text); version: Mapped[str]=mapped_column(String(40)); effective_date: Mapped[date]=mapped_column(Date); active: Mapped[bool]=mapped_column(default=True)

class Approval(Base, TimestampMixin):
    __tablename__="approvals"
    id: Mapped[uuid.UUID]=mapped_column(primary_key=True, default=uuid.uuid4); invoice_id: Mapped[uuid.UUID]=mapped_column(ForeignKey("invoices.id"), index=True)
    approver_id: Mapped[uuid.UUID|None]=mapped_column(ForeignKey("users.id"), nullable=True); approval_level: Mapped[str]=mapped_column(String(80)); status: Mapped[ApprovalStatus]=mapped_column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING)
    comments: Mapped[str|None]=mapped_column(Text, nullable=True)

class AuditLog(Base):
    __tablename__="audit_logs"
    id: Mapped[uuid.UUID]=mapped_column(primary_key=True, default=uuid.uuid4); invoice_id: Mapped[uuid.UUID|None]=mapped_column(ForeignKey("invoices.id"), nullable=True, index=True)
    user_id: Mapped[uuid.UUID|None]=mapped_column(ForeignKey("users.id"), nullable=True); request_id: Mapped[str]=mapped_column(String(100), index=True)
    actor_type: Mapped[str]=mapped_column(String(30)); agent: Mapped[str]=mapped_column(String(100)); action: Mapped[str]=mapped_column(String(120))
    input_summary: Mapped[dict]=mapped_column(JSON, default=dict); output_summary: Mapped[dict]=mapped_column(JSON, default=dict)
    timestamp: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

class WorkflowRun(Base, TimestampMixin):
    __tablename__="workflow_runs"
    id: Mapped[uuid.UUID]=mapped_column(primary_key=True, default=uuid.uuid4); invoice_id: Mapped[uuid.UUID]=mapped_column(ForeignKey("invoices.id"), index=True)
    status: Mapped[str]=mapped_column(String(40)); graph_version: Mapped[str]=mapped_column(String(40), default="1.0"); error_summary: Mapped[dict]=mapped_column(JSON, default=dict)

