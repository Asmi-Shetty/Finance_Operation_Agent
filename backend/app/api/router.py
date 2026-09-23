from fastapi import APIRouter
from app.api.v1.invoices import router as invoice_router
from app.api.v1.dashboard import router as dashboard_router
router=APIRouter()
router.include_router(invoice_router, prefix="/invoices", tags=["Invoices"])
router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])

