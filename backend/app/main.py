import time
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
import structlog
from app.api.router import router
from app.core.config import settings
from app.core.logging import configure_logging
from app.db.session import engine

configure_logging(); log=structlog.get_logger()
@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.upload_dir.mkdir(parents=True,exist_ok=True)
    yield
    await engine.dispose()

app=FastAPI(title=settings.app_name,version="0.1.0",lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=settings.cors_origins,allow_methods=["*"],allow_headers=["*"],allow_credentials=True)
@app.middleware("http")
async def request_context(request: Request,call_next):
    request.state.request_id=request.headers.get("X-Request-ID",str(uuid.uuid4())); started=time.perf_counter()
    response=await call_next(request); response.headers["X-Request-ID"]=request.state.request_id
    log.info("request.completed",request_id=request.state.request_id,method=request.method,path=request.url.path,status=response.status_code,latency_ms=round((time.perf_counter()-started)*1000,2))
    return response
@app.get("/health",tags=["Health"])
async def health(): return {"status":"ok","service":settings.app_name}
@app.get("/health/ready",tags=["Health"])
async def ready():
    async with engine.connect() as conn: await conn.execute(text("SELECT 1"))
    return {"status":"ready","database":"ok"}
app.include_router(router,prefix=settings.api_v1_prefix)
