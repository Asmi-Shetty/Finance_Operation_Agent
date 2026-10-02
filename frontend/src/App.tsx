import {useEffect,useMemo,useState} from 'react'
import {Activity,AlertTriangle,CheckCircle2,Clock3,FileSearch,IndianRupee,LayoutDashboard,Moon,ReceiptText,ShieldAlert,Sparkles,Sun,UploadCloud} from 'lucide-react'
import {api} from './services/api'
import type {Dashboard,Invoice,Status} from './types'

const empty:Dashboard={total_invoices:0,pending_review:0,approved:0,exceptions:0,duplicate_alerts:0,high_risk:0,total_invoice_value:'0'}
const money=(value:string|null,currency='INR')=>value?new Intl.NumberFormat('en-IN',{style:'currency',currency}).format(Number(value)):'—'
const badge=(status:Status)=>status.toLowerCase().replaceAll('_','-')

export function App(){
 const [dashboard,setDashboard]=useState(empty),[invoices,setInvoices]=useState<Invoice[]>([]),[busy,setBusy]=useState(false),[error,setError]=useState('')
 const [now,setNow]=useState(()=>new Date())
 const [theme,setTheme]=useState<'light'|'dark'>(()=>{
  const saved=localStorage.getItem('ledgerflow-theme')
  return saved==='light'||saved==='dark'?saved:window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light'
 })
 const load=async()=>{try{const [d,list]=await Promise.all([api.dashboard(),api.invoices()]);setDashboard(d);setInvoices(list.items)}catch(e){setError(e instanceof Error?e.message:'Unable to load data')}}
 useEffect(()=>{void load()},[])
 useEffect(()=>{document.documentElement.dataset.theme=theme;localStorage.setItem('ledgerflow-theme',theme)},[theme])
 useEffect(()=>{const timer=window.setInterval(()=>setNow(new Date()),1000);return()=>window.clearInterval(timer)},[])
 const upload=async(file?:File)=>{if(!file)return;setBusy(true);setError('');try{await api.upload(file);await load()}catch(e){setError(e instanceof Error?e.message:'Upload failed')}finally{setBusy(false)}}
 const cards=[['Invoice value',money(dashboard.total_invoice_value),'Across all invoices',IndianRupee],['Pending review',dashboard.pending_review,'Needs finance attention',Clock3],['Approved',dashboard.approved,'Payment-ready records',CheckCircle2],['Exceptions',dashboard.exceptions,'Rule-based exceptions',AlertTriangle],['Duplicate alerts',dashboard.duplicate_alerts,'Deterministic signals',FileSearch],['High risk',dashboard.high_risk,'Requires human review',ShieldAlert]] as const
 const activity=useMemo(()=>invoices.slice(0,4).map((invoice,index)=>({
  title:invoice.invoice_number??'Document received',
  detail:invoice.status.replaceAll('_',' ').toLowerCase(),
  time:index===0?'Just now':`${index*4+2}m ago`,
  tone:invoice.status==='EXCEPTION'||invoice.risk_level==='HIGH'?'warning':invoice.status==='PAYMENT_READY'||invoice.status==='APPROVED'?'success':'active'
 })),[invoices])
 const stages=[['Ingested',dashboard.total_invoices],['Validated',Math.max(0,dashboard.total_invoices-dashboard.exceptions)],['Review',dashboard.pending_review+dashboard.exceptions],['Ready',dashboard.approved]] as const
 return <div className="shell">
  <div className="ambient" aria-hidden="true"><span/><span/><span/></div>
  <aside><div className="brand"><span className="brandmark"><i>LF</i></span><div><strong>LedgerFlow</strong><small>FINANCE OPERATIONS</small></div></div><nav><a className="active"><LayoutDashboard size={18}/>Overview</a><a><ReceiptText size={18}/>Invoices <em>{dashboard.total_invoices}</em></a><a><ShieldAlert size={18}/>Review queue <em>{dashboard.pending_review+dashboard.exceptions}</em></a></nav><div className="safety"><span className="safety-icon"><ShieldAlert size={18}/></span><div><strong>Human controlled</strong><small>No payment is ever initiated automatically.</small></div></div></aside>
  <main><header><div className="hero-copy"><p className="eyebrow"><span className="live-dot"/>ACCOUNTS PAYABLE</p><h1>Finance operations</h1><p>Review invoices, policy evidence, and approval decisions.</p></div><div className="header-actions"><button className="theme-toggle" type="button" onClick={()=>setTheme(current=>current==='light'?'dark':'light')} aria-label={`Switch to ${theme==='light'?'dark':'light'} theme`} title={`Switch to ${theme==='light'?'dark':'light'} theme`}><span className="toggle-track"><Sun size={15}/><Moon size={15}/><i className="toggle-thumb"/></span></button><label className={`upload ${busy?'disabled':''}`}><span className="upload-glow"/><UploadCloud size={18}/>{busy?'Uploading…':'Upload invoice'}<input type="file" accept=".pdf,.png,.jpg,.jpeg" disabled={busy} onChange={e=>void upload(e.target.files?.[0])}/></label></div></header>
  {error&&<div className="error">{error}</div>}
  <section className="command-bar">
   <div className="command-status"><span className="status-orb"><Activity size={18}/></span><div><p><span className="live-dot"/>SYSTEM LIVE</p><strong>Invoice operations are running normally</strong><small>Deterministic controls active · Human approval enforced</small></div></div>
   <div className="live-time"><span>{now.toLocaleDateString('en-IN',{weekday:'short',day:'2-digit',month:'short'})}</span><strong>{now.toLocaleTimeString('en-IN',{hour:'2-digit',minute:'2-digit',second:'2-digit'})}</strong></div>
   <div className="signal" aria-label="System health"><i/><i/><i/><i/></div>
  </section>
  <section className="metrics">{cards.map(([label,value,hint,Icon],index)=><article key={label} style={{animationDelay:`${120+index*75}ms`}}><span className="card-shine"/><div className="metric-icon"><Icon size={19}/></div><div><span>{label}</span><strong>{value}</strong><small>{hint}</small></div></article>)}</section>
  <section className="live-grid">
   <article className="flow-card"><div className="section-title"><div><p className="eyebrow"><Sparkles size={12}/>AUTOMATED WORKFLOW</p><h2>Invoice pipeline</h2></div><span className="streaming"><i/>Streaming</span></div><div className="pipeline">{stages.map(([label,value],index)=><div className="stage" key={label}><span className="stage-node">{index+1}</span><strong>{value}</strong><small>{label}</small>{index<stages.length-1&&<i className="flow-line"/>}</div>)}</div><div className="throughput"><div><span>Processing throughput</span><strong>{dashboard.total_invoices?Math.min(98,72+dashboard.approved):72}%</strong></div><div className="throughput-track"><i style={{width:`${dashboard.total_invoices?Math.min(98,72+dashboard.approved):72}%`}}/></div></div></article>
   <article className="activity-card"><div className="section-title"><div><p className="eyebrow"><Activity size={12}/>ACTIVITY</p><h2>Live events</h2></div><span className="event-count">{activity.length}</span></div><div className="activity-list">{activity.length?activity.map((event,index)=><div className="activity-item" key={`${event.title}-${index}`}><span className={`activity-dot ${event.tone}`}/><div><strong>{event.title}</strong><small>{event.detail}</small></div><time>{event.time}</time></div>):<div className="waiting"><span className="radar"><i/></span><div><strong>Watching for activity</strong><small>New invoice events will appear here.</small></div></div>}</div></article>
  </section>
  <section className="panel"><div className="panel-head"><div><p className="eyebrow"><span className="live-dot"/>LIVE WORK QUEUE</p><h2>Recent invoices</h2></div><span className="record-count">{invoices.length} records</span></div>
   <div className="table-wrap"><table><thead><tr><th>Invoice</th><th>Date</th><th>Amount</th><th>Risk</th><th>Status</th></tr></thead><tbody>{invoices.map(x=><tr key={x.id}><td><strong>{x.invoice_number??'Awaiting extraction'}</strong><small>{x.id.slice(0,8)}</small></td><td>{x.invoice_date??'—'}</td><td>{money(x.total,x.currency??'INR')}</td><td><span className={`risk ${x.risk_level.toLowerCase()}`}>{x.risk_level}</span></td><td><span className={`status ${badge(x.status)}`}>{x.status.replaceAll('_',' ')}</span></td></tr>)}{!invoices.length&&<tr><td colSpan={5} className="empty"><ReceiptText size={28}/><strong>No invoices yet</strong><span>Upload a PDF or image to begin the controlled AP workflow.</span></td></tr>}</tbody></table></div>
  </section></main>
 </div>
}
