import type {Dashboard,Invoice} from '../types'
const BASE=import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1'
async function request<T>(path:string,options?:RequestInit):Promise<T>{const response=await fetch(`${BASE}${path}`,options);if(!response.ok){const problem=await response.json().catch(()=>({detail:'Request failed'}));throw new Error(problem.detail??'Request failed')}return response.json()}
export const api={
 dashboard:()=>request<Dashboard>('/dashboard'),
 invoices:()=>request<{items:Invoice[];total:number}>('/invoices'),
 upload:(file:File)=>{const body=new FormData();body.append('file',file);return request<{invoice_id:string}>('/invoices/upload',{method:'POST',body})},
 action:(id:string,action:'approve'|'reject'|'request-clarification',comments='')=>request(`/invoices/${id}/${action}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({comments})})
}

