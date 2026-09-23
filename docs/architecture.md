# Architecture

```mermaid
flowchart LR
  UI[React Finance Console] --> API[FastAPI]
  API --> G[LangGraph Orchestrator]
  G --> X[Document Extraction]
  G --> P[PO Match]
  G --> R[Policy Retrieval]
  G --> D[Duplicate Detection]
  G --> A[Anomaly Rules]
  G --> E[Decision Engine]
  E --> H[Human Approval]
  H --> PR[Payment Ready]
  API --> DB[(PostgreSQL + pgvector)]
  G --> DB
  G --> REDIS[(Redis)]
```

The graph coordinates bounded tools. It does not confer decision authority on the LLM. Calculation, validation, decision, approval routing, and state transitions are ordinary tested code.

## Workflow states

`UPLOADED → PROCESSING → VALIDATED/EXCEPTION → PENDING_APPROVAL → PAYMENT_READY`

Human reviewers may instead move an awaiting record to `REJECTED` or `CLARIFICATION_REQUESTED`. `PAID` is reserved for a future authorized ERP integration and cannot be reached by the MVP.

