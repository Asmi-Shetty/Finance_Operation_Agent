import hashlib
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.db.session import get_session
from app.models.entities import Approval, ApprovalStatus, AuditLog, Invoice, InvoiceDocument, InvoiceStatus
from app.schemas.invoice import ActionResponse, ApprovalRequest, InvoiceList, InvoiceSummary, UploadResponse

router=APIRouter()
ALLOWED={"application/pdf":".pdf", "image/png":".png", "image/jpeg":".jpg"}

async def audit(session, request, invoice_id, action, output):
    session.add(AuditLog(invoice_id=invoice_id, request_id=getattr(request.state,"request_id","unknown"), actor_type="USER", agent="api", action=action, output_summary=output))

@router.post("/upload", response_model=UploadResponse, status_code=201)
async def upload_invoice(request: Request, file: UploadFile=File(...), session: AsyncSession=Depends(get_session)):
    if file.content_type not in ALLOWED:
        raise HTTPException(415, "Only PDF, PNG, JPG and JPEG invoices are accepted")
    data=await file.read(settings.max_upload_bytes+1)
    if not data or len(data)>settings.max_upload_bytes:
        raise HTTPException(413, "File is empty or exceeds upload limit")
    signatures={"application/pdf":b"%PDF", "image/png":b"\x89PNG", "image/jpeg":b"\xff\xd8\xff"}
    if not data.startswith(signatures[file.content_type]):
        raise HTTPException(400, "File content does not match declared type")
    digest=hashlib.sha256(data).hexdigest(); invoice=Invoice(status=InvoiceStatus.UPLOADED)
    session.add(invoice); await session.flush()
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    safe_name=f"{invoice.id}{ALLOWED[file.content_type]}"; path=settings.upload_dir/safe_name
    path.write_bytes(data)
    session.add(InvoiceDocument(invoice_id=invoice.id,file_name=Path(file.filename or "invoice").name,storage_key=safe_name,media_type=file.content_type,document_hash=digest))
    await audit(session,request,invoice.id,"invoice.uploaded",{"file_name":Path(file.filename or "invoice").name,"sha256":digest})
    await session.commit()
    return UploadResponse(invoice_id=invoice.id,status=invoice.status,file_name=Path(file.filename or "invoice").name,document_hash=digest)

@router.get("", response_model=InvoiceList)
async def list_invoices(page: int=Query(1,ge=1), page_size: int=Query(25,ge=1,le=100), status: InvoiceStatus|None=None, session: AsyncSession=Depends(get_session)):
    predicate=[] if status is None else [Invoice.status==status]
    total=await session.scalar(select(func.count()).select_from(Invoice).where(*predicate))
    rows=(await session.scalars(select(Invoice).where(*predicate).order_by(Invoice.created_at.desc()).offset((page-1)*page_size).limit(page_size))).all()
    return InvoiceList(items=[InvoiceSummary.model_validate(x) for x in rows],total=total or 0,page=page,page_size=page_size)

@router.get("/{invoice_id}", response_model=InvoiceSummary)
async def get_invoice(invoice_id: uuid.UUID, session: AsyncSession=Depends(get_session)):
    invoice=await session.get(Invoice,invoice_id)
    if not invoice: raise HTTPException(404,"Invoice not found")
    return invoice

@router.post("/{invoice_id}/process", response_model=ActionResponse)
async def process_invoice(invoice_id: uuid.UUID, request: Request, session: AsyncSession=Depends(get_session)):
    invoice=await session.get(Invoice,invoice_id)
    if not invoice: raise HTTPException(404,"Invoice not found")
    if invoice.status not in {InvoiceStatus.UPLOADED,InvoiceStatus.EXCEPTION,InvoiceStatus.CLARIFICATION_REQUESTED}:
        raise HTTPException(409,"Invoice cannot be processed from its current state")
    invoice.status=InvoiceStatus.PROCESSING
    await audit(session,request,invoice.id,"workflow.queued",{"status":invoice.status.value}); await session.commit()
    return ActionResponse(invoice_id=invoice.id,status=invoice.status,message="Invoice queued for processing")

@router.post("/{invoice_id}/validate", response_model=ActionResponse)
async def validate_invoice(invoice_id: uuid.UUID, request: Request, session: AsyncSession=Depends(get_session)):
    invoice=await session.get(Invoice,invoice_id)
    if not invoice: raise HTTPException(404,"Invoice not found")
    complete=all([invoice.invoice_number,invoice.invoice_date,invoice.total is not None,invoice.currency])
    invoice.status=InvoiceStatus.VALIDATED if complete else InvoiceStatus.EXCEPTION
    await audit(session,request,invoice.id,"invoice.validated",{"valid":complete}); await session.commit()
    return ActionResponse(invoice_id=invoice.id,status=invoice.status,message="Validation completed")

@router.get("/{invoice_id}/analysis")
async def analysis(invoice_id: uuid.UUID, session: AsyncSession=Depends(get_session)):
    invoice=await session.get(Invoice,invoice_id)
    if not invoice: raise HTTPException(404,"Invoice not found")
    return {"invoice_id":invoice.id,"status":invoice.status,"risk":{"level":invoice.risk_level,"score":invoice.anomaly_score},"message":"Analysis becomes available as workflow nodes complete"}

async def approval_action(invoice_id, request, body, target, event, session):
    invoice=await session.get(Invoice,invoice_id)
    if not invoice: raise HTTPException(404,"Invoice not found")
    if invoice.status not in {InvoiceStatus.PENDING_APPROVAL,InvoiceStatus.EXCEPTION}:
        raise HTTPException(409,"Invoice is not awaiting a human decision")
    if target in {InvoiceStatus.REJECTED,InvoiceStatus.CLARIFICATION_REQUESTED} and not body.comments:
        raise HTTPException(422,"Comments are required for this action")
    invoice.status=target
    session.add(Approval(invoice_id=invoice.id,approval_level="FINANCE",status=ApprovalStatus(target.value if target!=InvoiceStatus.PAYMENT_READY else "APPROVED"),comments=body.comments))
    await audit(session,request,invoice.id,event,{"status":target.value,"comments_provided":bool(body.comments)}); await session.commit()
    return ActionResponse(invoice_id=invoice.id,status=target,message=event.replace("."," ").title())

@router.post("/{invoice_id}/approve",response_model=ActionResponse)
async def approve(invoice_id: uuid.UUID,request: Request,body: ApprovalRequest,session: AsyncSession=Depends(get_session)):
    return await approval_action(invoice_id,request,body,InvoiceStatus.PAYMENT_READY,"invoice.approved",session)
@router.post("/{invoice_id}/reject",response_model=ActionResponse)
async def reject(invoice_id: uuid.UUID,request: Request,body: ApprovalRequest,session: AsyncSession=Depends(get_session)):
    return await approval_action(invoice_id,request,body,InvoiceStatus.REJECTED,"invoice.rejected",session)
@router.post("/{invoice_id}/request-clarification",response_model=ActionResponse)
async def clarify(invoice_id: uuid.UUID,request: Request,body: ApprovalRequest,session: AsyncSession=Depends(get_session)):
    return await approval_action(invoice_id,request,body,InvoiceStatus.CLARIFICATION_REQUESTED,"invoice.clarification_requested",session)

@router.get("/{invoice_id}/audit")
async def invoice_audit(invoice_id: uuid.UUID,session: AsyncSession=Depends(get_session)):
    if not await session.get(Invoice,invoice_id): raise HTTPException(404,"Invoice not found")
    events=(await session.scalars(select(AuditLog).where(AuditLog.invoice_id==invoice_id).order_by(AuditLog.timestamp))).all()
    return [{"id":x.id,"agent":x.agent,"action":x.action,"output":x.output_summary,"timestamp":x.timestamp} for x in events]

