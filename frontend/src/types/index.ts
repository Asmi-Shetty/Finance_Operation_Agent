export type Status='UPLOADED'|'PROCESSING'|'VALIDATED'|'EXCEPTION'|'PENDING_APPROVAL'|'APPROVED'|'REJECTED'|'CLARIFICATION_REQUESTED'|'PAYMENT_READY'|'PAID'
export interface Invoice {id:string;invoice_number:string|null;invoice_date:string|null;due_date:string|null;subtotal:string|null;tax:string|null;total:string|null;currency:string|null;status:Status;risk_level:'LOW'|'MEDIUM'|'HIGH';anomaly_score:string;created_at:string}
export interface Dashboard {total_invoices:number;pending_review:number;approved:number;exceptions:number;duplicate_alerts:number;high_risk:number;total_invoice_value:string}

