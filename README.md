# LedgerFlow — AI Finance Operations Agent

A production-oriented Accounts Payable automation MVP. AI is used for document extraction and grounded policy assistance; monetary calculations, validation, workflow routing, and approval controls remain deterministic.

## Run with Docker

1. Copy `.env.example` to `.env`.
2. Run `docker compose up --build`.
3. Open the finance console at `http://localhost:5173`.
4. Open the API documentation at `http://localhost:8000/docs`.

The stack starts React, FastAPI, PostgreSQL with pgvector, and Redis. No LLM key is necessary for the deterministic foundation or local mock path.

## Local backend development

From `backend/`, install Python 3.12 and run:

```bash
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
pytest
```

Without `DATABASE_URL`, the backend uses local SQLite. Production and Docker use PostgreSQL.

## Safety invariants

- All money uses `Decimal` and fixed-precision database columns.
- The LLM cannot set workflow status or approve an invoice.
- Policy responses must be grounded in retrieved, versioned sources.
- Duplicate, PO, threshold, and decision checks are deterministic.
- Human approval is required before `PAYMENT_READY`.
- There is no payment execution endpoint.
- Logs contain metadata and redacted summaries, not document bodies or sensitive banking data.

See [architecture](docs/architecture.md) and [API notes](docs/api.md).

