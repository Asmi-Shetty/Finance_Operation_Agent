# API

The OpenAPI contract is generated at `/docs`. All workflow endpoints are under `/api/v1`.

- `POST /invoices/upload`
- `GET /invoices`
- `GET /invoices/{invoice_id}`
- `POST /invoices/{invoice_id}/process`
- `POST /invoices/{invoice_id}/validate`
- `GET /invoices/{invoice_id}/analysis`
- `POST /invoices/{invoice_id}/approve`
- `POST /invoices/{invoice_id}/reject`
- `POST /invoices/{invoice_id}/request-clarification`
- `GET /invoices/{invoice_id}/audit`
- `GET /dashboard`
- `GET /health`
- `GET /health/ready`

Mutations are audited. Rejection and clarification require comments. Approval produces `PAYMENT_READY`; it never executes payment.
