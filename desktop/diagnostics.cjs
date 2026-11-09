const crypto=require('node:crypto');
const TTL=30*60*1000;
function classify(raw,updates=null,updateError=false){
  const findings=[];
  const add=(id,category,status,reason,evidence={},actions=[])=>findings.push({id,category,status,reason,evidence,actions});
  const unavailable=new Set(raw.unavailable||[]);
  for(const category of unavailable)add(`unavailable:${category}`,category,'unknown','unavailable');
  if(!unavailable.has('devices')){
    let disconnected=0,healthy=0;
    for(const d of raw.devices||[]){
      if(d.present===false||d.code===45){disconnected++;continue;}
      const evidence={name:d.name||d.id,code:d.code,version:d.version||'',provider:d.provider||''};
      if(d.code===22){add(`device:${d.id}`,'devices','info','disabled',evidence,[{id:'devices',kind:'guide'}]);continue;}
      if(!Number.isInteger(d.code)){add(`device:${d.id}`,'devices','unknown','deviceUnknown',evidence);continue;}
      if(d.code!==0){add(`device:${d.id}`,'devices','issue',d.code===28?'missingDriver':'deviceError',evidence,[{id:'device-rescan',kind:'repair'},{id:'drivers',kind:'navigate'},{id:'devices',kind:'guide'}]);continue;}
      healthy++;
    }
    add('devices:summary','devices','info','deviceSummary',{healthy,disconnected});
  }
  if(!unavailable.has('audio'))for(const s of raw.audio||[]){
    const stopped=s.status!=='Running',disabled=s.startType==='Disabled';
    add(`audio:${s.id}`,'audio',stopped&&!disabled?'issue':'info',disabled?'audioDisabled':stopped?'audioStopped':'audioRunning',{name:s.id,status:s.status,startType:s.startType},stopped&&!disabled?[{id:'audio-start',kind:'repair'},{id:'sound',kind:'guide'}]:[{id:'sound',kind:'guide'}]);
  }
  if(!unavailable.has('network')&&raw.network){
    const up=(raw.network.adapters||[]).filter(a=>a.status==='Up');
    add('network:link','network','info',up.length?'networkUp':'networkOffline',{count:up.length},[{id:'network-settings',kind:'guide'}]);
    if(raw.network.dnsChecked)add('network:dns','network',raw.network.dnsOk===true?'info':'issue',raw.network.dnsOk===true?'dnsOk':'dnsFailed',{},raw.network.dnsOk===true?[]:[{id:'dns-flush',kind:'repair'},{id:'network-settings',kind:'guide'}]);
    else add('network:dns-skipped','network','info','dnsSkipped');
  }
  if(!unavailable.has('display'))for(const [i,d] of (raw.display||[]).entries()){
    const basic=(raw.devices||[]).some(p=>p.deviceClass==='Display'&&p.name===d.name&&/^BasicDisplay$/i.test(p.service||''))||/basicdisplay/i.test(d.service||'')||/Microsoft Basic Display Adapter/i.test(d.name||'');
    add(`display:${i}`,'display',basic?'issue':'info',basic?'basicDisplay':'displayInfo',{name:d.name||'',width:d.width||0,height:d.height||0},[{id:'display',kind:'guide'},{id:'drivers',kind:'navigate'}]);
  }
  if(!unavailable.has('runtimes'))for(const r of raw.runtimes||[])add(`runtime:${r.id}`,'runtimes',r.installed?'info':'optional',r.installed?'runtimePresent':'runtimeOptional',{name:r.id==='directx-legacy'?'DirectX (D3DX9 / XAudio 2.7)':`Visual C++ v14 (${r.id.slice(3)})`,version:r.version||''},r.installed?[]:[{id:r.id==='directx-legacy'?'directx':'visual-cpp',kind:'guide'}]);
  if(updates!==null)for(const u of updates)add(`update:${u.id}`,'devices','update','driverUpdate',{name:u.name,bytes:u.bytes,manufacturer:u.manufacturer},[{id:'drivers',kind:'navigate'}]);
  if(updates!==null&&!updates.length)add('updates:none','devices','info','noUpdates');
  if(updateError)add('updates:unknown','devices','unknown','updateUnavailable');
  return findings;
}
function verified(finding,raw){
  if((raw.unavailable||[]).includes(finding.category))return null;
  if(finding.id.startsWith('audio:')){const service=raw.audio?.find(s=>`audio:${s.id}`===finding.id);return service?service.status==='Running':null;}
  if(finding.id==='network:dns')return raw.network?.dnsChecked===true?raw.network.dnsOk===true:null;
  if(finding.id.startsWith('device:')){const device=raw.devices?.find(d=>`device:${d.id}`===finding.id);return device&&device.present!==false&&device.code!==45&&Number.isInteger(device.code)?device.code===0:null;}
  return null;
}
class Diagnostics {
  constructor(native,record,now=Date.now,persist=()=>{}){this.native=native;this.record=record;this.now=now;this.persist=persist;this.report=null;}
  async scan(payload={}){
    const online=payload.online===true;
    const raw=await this.native('diagnostics',{online});let updates=null,updateError=false;
    if(online)try{updates=await this.native('windows-updates')||[];}catch{updateError=true;}
    this.report={id:crypto.randomUUID(),at:new Date(this.now()).toISOString(),online,findings:classify(raw,updates,updateError)};
    this.created=this.now();return this.report;
  }
  async repair(payload){
    if(payload.confirm!==true)throw Error('CONFIRM_REQUIRED');
    const report=this.report;
    if(!report||report.id!==payload.reportId||this.now()-this.created>TTL)throw Error('SCAN_EXPIRED');
    const finding=report.findings.find(f=>f.id===payload.findingId);
    const action=finding?.actions.find(a=>a.id===payload.actionId&&a.kind==='repair');
    if(!action)throw Error('INVALID_SELECTION');
    // Recheck the exact finding before mutation. A disabled, disconnected, or changed device isn't a repair target.
    const before=await this.native('diagnostics',{online:report.online});
    const current=classify(before).find(f=>f.id===finding.id&&f.status==='issue'&&f.actions.some(a=>a.id===action.id&&a.kind==='repair'));
    if(!current)throw Error('DIAGNOSTIC_CHANGED');
    const target=action.id==='audio-start'?finding.id.slice('audio:'.length):undefined;
    const event=this.record('diagnostics-repair',{findingId:finding.id,action:action.id,name:finding.evidence.name||'',status:'pending',success:false});
    this.report=null; // One-shot repair plans; further actions require a fresh report.
    try {
      await this.native('diagnostic-repair',{kind:action.id,target},action.id!=='dns-flush');
      const after=await this.native('diagnostics',{online:report.online});const check=verified(finding,after);
      const result={success:check===true,status:check===true?'fixed':check===false?'still-present':'unverified',findingId:finding.id,action:action.id,at:new Date(this.now()).toISOString()};
      Object.assign(event,result);this.persist();
      // Preserve the optional online update results. Only the local checks are refreshed here.
      this.report={...report,id:crypto.randomUUID(),at:result.at,findings:[...classify(after),...report.findings.filter(f=>f.reason==='driverUpdate'||f.reason==='noUpdates'||f.reason==='updateUnavailable')]};this.created=this.now();
      return {...result,report:this.report};
    }catch(error){event.status='failed';this.persist();throw error;}
  }
}
module.exports={Diagnostics,classify,verified,TTL};
