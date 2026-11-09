import React,{useEffect,useRef,useState} from 'react';
import {Search,Wrench,ExternalLink,Download,CheckCircle2,TriangleAlert,ShieldCheck} from 'lucide-react';
import {diagnosticsText,type DiagnosticKey} from './diagnostics-i18n';
type Action={id:string;kind:'repair'|'guide'|'navigate'};
type Finding={id:string;category:DiagnosticKey;status:DiagnosticKey;reason:DiagnosticKey;evidence:Record<string,string|number>;actions:Action[]};
export type DiagnosticReport={id:string;at:string;online:boolean;findings:Finding[]};
type Props={onVerifiedRepair:()=>void;report:DiagnosticReport|null;setReport:(report:DiagnosticReport)=>void;language:'tr'|'en';busy:boolean;perform:(command:string,payload?:any,callback?:(value:any)=>void,showSuccess?:boolean)=>Promise<void>;navigate:(destination?:string)=>void;companion:React.ReactNode};
const actionKeys:Record<string,DiagnosticKey>={'device-rescan':'rescan','audio-start':'audioStart','dns-flush':'dnsFlush',drivers:'goDrivers',sound:'sound',display:'displayAction','network-settings':'networkAction',devices:'devicesAction','visual-cpp':'vcAction',runtimes:'goRuntimes',directx:'dxAction'};
export function ScanFix({onVerifiedRepair,report,setReport,language,busy,perform,navigate,companion}:Props){
  const t=(key:DiagnosticKey)=>diagnosticsText[language][key];
  const [online,setOnline]=useState(false),[status,setStatus]=useState('all'),[category,setCategory]=useState('all'),[result,setResult]=useState<string|null>(null),[manual,setManual]=useState(false),[pending,setPending]=useState<{finding:Finding;action:Action}|null>(null);
  const dialog=useRef<HTMLDialogElement>(null);
  useEffect(()=>{if(pending)dialog.current?.showModal();else dialog.current?.close();},[pending]);
  const scan=()=>{setResult(null);setManual(false);void perform('diagnostics.scan',{online},value=>setReport(value),false);};
  const statuses:DiagnosticKey[]=['issue','update','optional','unknown','info'];
  const categories:DiagnosticKey[]=['devices','audio','network','display','runtimes'];
  const findings=report?.findings.filter(f=>(status==='all'||f.status===status)&&(category==='all'||f.category===category))||[];
  function action(finding:Finding,a:Action){if(a.kind==='repair'){setPending({finding,action:a});return;}if(a.kind==='navigate'){navigate(a.id);return;}setManual(true);void perform('external',{id:a.id},undefined,false);}
  return <>
    <div className="page-heading"><div><h1>{t('title')}</h1><p>{t('intro')}</p></div><Wrench size={30}/></div>
    <section className={`hero diagnostics-hero ${!companion?'no-companion':''}`}><div className="hero-copy"><h2>{t('title')}</h2><p>{t('localHelp')}</p><label className="diagnostic-option"><input type="checkbox" checked={online} disabled={busy} onChange={e=>setOnline(e.target.checked)}/><strong>{t('online')}</strong></label><p className="muted">{t('onlineHelp')}</p><div className="actions"><button className="button primary" disabled={busy} onClick={scan}><Search size={18}/>{t(report?'again':'scan')}</button>{report&&<button className="button" disabled={busy} onClick={()=>void perform('report.export',{},undefined,false)}><Download size={18}/>{t('export')}</button>}</div></div>{companion}</section>
    <p className="notice"><ShieldCheck size={20}/>{t('coverage')}</p>
    {result&&<div role="status" className={`notice ${result==='fixed'?'diagnostic-fixed':''}`}>{result==='fixed'?<CheckCircle2 size={20}/>:<TriangleAlert size={20}/>}<span><strong>{t(result==='fixed'?'fixed':result==='still-present'?'still':'unverified')}</strong><br/>{t('recheck')}</span></div>}
    {manual&&<p className="notice" role="status">{t('manual')}</p>}
    {!report?<section className="card empty-state"><Search size={30}/><p>{t('empty')}</p></section>:<>
      <div className="diagnostic-summary">{statuses.map(s=><button className={`card diagnostic-count ${s==='issue'?'warning':''}`} key={s} aria-pressed={status===s} onClick={()=>setStatus(status===s?'all':s)}><strong>{report.findings.filter(f=>f.status===s).length}</strong><span>{t(s)}</span></button>)}</div>
      <p className="muted">{t('at')}: {new Date(report.at).toLocaleString(language==='tr'?'tr-TR':'en-US')}{!report.online&&<> • {t('onlineOff')}</>}</p>
      <div className="actions diagnostic-filters"><label>{t('filter')}<select value={status} onChange={e=>setStatus(e.target.value)}><option value="all">{t('all')}</option>{statuses.map(s=><option key={s} value={s}>{t(s)}</option>)}</select></label><label>{t('category')}<select value={category} onChange={e=>setCategory(e.target.value)}><option value="all">{t('all')}</option>{categories.map(c=><option key={c} value={c}>{t(c)}</option>)}</select></label></div>
      <div className="diagnostic-results">{!findings.length&&<p className="card">{t('noFilter')}</p>}{findings.map(f=><section className="card" key={f.id}>
        <div className="section-heading"><h2>{f.evidence.name||t(f.category)}</h2><span className={`pill ${f.status==='issue'?'warning':f.status==='info'?'good':''}`}>{t(f.status)}</span></div>
        <p>{t(f.reason)}</p>
        {Object.keys(f.evidence).length>0&&<details><summary>{t('evidence')}</summary><dl className="facts">{Object.entries(f.evidence).map(([key,value])=><div key={key}><dt>{t(key as DiagnosticKey)||key}</dt><dd>{value===''?'—':String(value)}</dd></div>)}</dl></details>}
        {f.actions.some(a=>a.kind==='navigate')&&<p className="muted">{t('updateGuide')}</p>}
        <div className="actions">{f.actions.map(a=><button className={a.kind==='repair'?'button primary':'button'} disabled={busy} key={a.id} onClick={()=>action(f,a)}>{a.kind==='repair'?<Wrench size={17}/>:<ExternalLink size={17}/>} {t(actionKeys[a.id])}</button>)}</div>
      </section>)}</div>
    </>}
    <details className="card"><summary>{t('evidence')}</summary><p>{t('scope')}</p></details>
    <dialog ref={dialog} onCancel={()=>setPending(null)} aria-labelledby="diagnostic-confirm-title"><h2 id="diagnostic-confirm-title">{t('confirm')}</h2><p><strong>{pending?.finding.evidence.name||t('network')}</strong></p><p>{t(pending?.action.id==='audio-start'?'audioImpact':pending?.action.id==='dns-flush'?'dnsImpact':'deviceImpact')}</p><div className="actions"><button className="button" onClick={()=>setPending(null)}>{t('cancel')}</button><button className="button primary" disabled={busy} onClick={()=>{if(!pending||!report)return;const payload={reportId:report.id,findingId:pending.finding.id,actionId:pending.action.id,confirm:true};setPending(null);setResult(null);void perform('diagnostics.repair',payload,value=>{setReport(value.report);setResult(value.status);if(value.success===true&&value.status==='fixed')onVerifiedRepair();},false);}}>{t('continue')}</button></div></dialog>
  </>;
}
