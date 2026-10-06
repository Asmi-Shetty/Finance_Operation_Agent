import type {Dashboard,Invoice} from '../types'

const BASE=import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1'
const DEMO_KEY='ledgerflow-demo-invoices'
let offline=false

function readDemoInvoices():Invoice[]{
 try{return JSON.parse(localStorage.getItem(DEMO_KEY)??'[]') as Invoice[]}
 catch{return []}
}

function writeDemoInvoices(invoices:Invoice[]){localStorage.setItem(DEMO_KEY,JSON.stringify(invoices))}

function demoDashboard():Dashboard{
 const invoices=readDemoInvoices()
 return {
  total_invoices:invoices.length,
  pending_review:invoices.filter(x=>x.status==='PENDING_APPROVAL').length,
  approved:invoices.filter(x=>x.status==='APPROVED'||x.status==='PAYMENT_READY').length,
  exceptions:invoices.filter(x=>x.status==='EXCEPTION').length,
  duplicate_alerts:0,
  high_risk:invoices.filter(x=>x.risk_level==='HIGH').length,
  total_invoice_value:String(invoices.reduce((sum,x)=>sum+Number(x.total??0),0))
 }
}

async function request<T>(path:string,options?:RequestInit):Promise<T>{
 try{
  const response=await fetch(`${BASE}${path}`,options)
  if(!response.ok){
   const problem=await response.json().catch(()=>({detail:'Request failed'}))
   throw new Error(problem.detail??'Request failed')
  }
  offline=false
  return response.json()
 }catch(error){
  if(error instanceof TypeError){offline=true;throw new TypeError('API_OFFLINE')}
  throw error
 }
}

async function withOfflineFallback<T>(live:()=>Promise<T>,fallback:()=>T|Promise<T>):Promise<T>{
 try{return await live()}
 catch(error){if(error instanceof TypeError&&error.message==='API_OFFLINE')return fallback();throw error}
}

export const api={
 isOffline:()=>offline,
 dashboard:()=>withOfflineFallback(()=>request<Dashboard>('/dashboard'),demoDashboard),
 invoices:()=>withOfflineFallback(()=>request<{items:Invoice[];total:number}>('/invoices'),()=>{
  const items=readDemoInvoices()
  return {items,total:items.length}
 }),
 upload:(file:File)=>withOfflineFallback(()=>{
  const body=new FormData();body.append('file',file)
  return request<{invoice_id:string}>('/invoices/upload',{method:'POST',body})
 },()=>{
  const id=crypto.randomUUID()
  const invoice:Invoice={id,invoice_number:file.name.replace(/\.[^.]+$/,''),invoice_date:new Date().toISOString().slice(0,10),due_date:null,subtotal:null,tax:null,total:null,currency:'INR',status:'UPLOADED',risk_level:'LOW',anomaly_score:'0',created_at:new Date().toISOString()}
  writeDemoInvoices([invoice,...readDemoInvoices()])
  return {invoice_id:id}
 }),
 action:(id:string,action:'approve'|'reject'|'request-clarification',comments='')=>request(`/invoices/${id}/${action}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({comments})})
}
