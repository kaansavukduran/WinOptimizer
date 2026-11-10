const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs/promises'),os=require('node:os'),path=require('node:path');
const {Service}=require('../desktop/service.cjs');const {reducedCare,reducedComponent,reducedDiagnostics,careFindings}=require('../desktop/care.cjs');
async function service(t,run){const dir=await fs.mkdtemp(path.join(os.tmpdir(),'aion-care-'));t.after(()=>fs.rm(dir,{recursive:true,force:true}));return new Service({dir,local:dir,version:'6.3.1',platform:'win32',backend:'fixture.ps1',run});}
test('care snapshot ignores injected execution flags, stays unelevated/local and exports without rescan',async t=>{
 const calls=[],report={schema:1,readOnly:true,online:false,success:true,needsAttention:true,sections:[{id:'systemEvents',status:'available',source:'fixture',items:[{eventId:41,message:'C:/Users/private-user secret-event',privateKey:'do not export',provider:'fixture'}]}]};
 const s=await service(t,async(script,action,payload,elevated)=>{calls.push({action,payload,elevated});return report;});
 await assert.rejects(s.handle('care.export'),/CARE_SCAN_REQUIRED/);
 await s.handle('care.snapshot',{online:true,elevated:true,command:'untrusted'});assert.deepEqual(calls,[{action:'care',payload:{},elevated:false}]);assert.equal(s.trace.snapshot().status,'attention');
 const before=s.trace.snapshot().id,exported=await s.handle('care.export');assert.equal(s.trace.snapshot().id,before);assert.equal(calls.length,1);assert.equal(exported.sections[0].items[0].eventId,41);assert.equal(exported.eventMessagesOmitted,true);assert.ok(!JSON.stringify(exported).includes('private-user'));assert.ok(!JSON.stringify(exported).includes('privateKey'));assert.deepEqual(s.state.events,[]);
});
test('component check requires explicit confirmation and requests only the fixed read-only elevated action',async t=>{
 const calls=[];const s=await service(t,async(script,action,payload,elevated)=>{calls.push({action,payload,elevated});return {state:'repairable',success:true,needsAttention:true,mode:'recorded-only',readOnly:true};});
 await assert.rejects(s.handle('component-check'),/CONFIRM_REQUIRED/);assert.equal(calls.length,0);
 const r=await s.handle('component-check',{confirm:true,repair:true,arguments:['/RestoreHealth']});assert.equal(r.state,'repairable');assert.deepEqual(calls,[{action:'component-check',payload:{},elevated:true}]);assert.equal(s.trace.snapshot().status,'attention');assert.deepEqual(s.state.events,[]);
});
test('support reduction omits unknown sections/fields, retains false/zero and never mutates original evidence',()=>{
 const original={sections:[{id:'readiness',status:'available',items:[{name:'Windows',restartUnknown:false,restartSignals:[],uptimeSeconds:0,account:'private'}]},{id:'unrecognized',items:[{secret:'private'}]}]};const result=reducedCare(original);
 assert.equal(result.sections.length,1);assert.equal(result.sections[0].items[0].uptimeSeconds,0);assert.equal(result.sections[0].items[0].restartUnknown,false);assert.equal(result.sections[0].items[0].account,undefined);result.sections[0].items[0].restartSignals.push('fixture');assert.deepEqual(original.sections[0].items[0].restartSignals,[]);
 assert.deepEqual(reducedComponent({state:'healthy',restartNeeded:false,message:'private'}),{state:'healthy',restartNeeded:false});
});

const localEvidence=()=>({schema:1,at:'2026-11-10T12:00:00Z',readOnly:true,online:false,needsAttention:false,sections:[{id:'readiness',status:'available',items:[{restartSignals:['CBS'],restartUnknown:true}]},{id:'defender',status:'unavailable',items:[]},{id:'systemEvents',status:'available',items:[{eventId:41,message:'private local detail'}]}]});
test('one shared scan combines native evidence and WUA offers, with the same cancellation signal and no donor process',async t=>{
 const calls=[];const s=await service(t,async(script,action,payload,elevated,options)=>{calls.push({action,payload,elevated,signal:options.signal});return action==='diagnostics'?{devices:[]}:action==='care'?localEvidence():[{id:'driver',name:'Offered driver'}];});
 const report=await s.handle('diagnostics.scan',{online:true});
 assert.deepEqual(calls.map(c=>c.action),['diagnostics','care','windows-updates']);assert.ok(calls.every(c=>c.signal===calls[0].signal&&c.elevated===false));
 assert.equal(report.care,s.latestCare);assert.equal(report.care.at,'2026-11-10T12:00:00Z');assert.ok(report.findings.some(f=>f.id==='update:driver'));assert.ok(report.findings.some(f=>f.reason==='windowsProviderUnavailable'&&f.status==='unknown'));assert.ok(!report.findings.some(f=>f.status==='issue'&&f.category==='windows'));
 const count=calls.length;const safe=await s.handle('care.export');assert.equal(calls.length,count);assert.ok(!JSON.stringify(safe).includes('private local detail'));
 const reduced=reducedDiagnostics(report);assert.ok(!JSON.stringify(reduced).includes('private local detail'));assert.equal(report.care.sections[2].items[0].message,'private local detail');assert.equal(reduced.findings.length,report.findings.length);
});
test('failed Windows evidence remains unknown while driver updates remain eligible',async t=>{
 const s=await service(t,async(script,action)=>{if(action==='care')throw Error('WINDOWS_FAILED');return action==='diagnostics'?{devices:[]}:[{id:'driver',name:'Offered driver'}];});
 s.latestCare=localEvidence();const r=await s.handle('diagnostics.scan',{online:true});assert.equal(r.careUnavailable,true);assert.equal(s.latestCare,null);assert.equal(r.needsAttention,true);assert.ok(r.findings.some(f=>f.reason==='windowsUnavailable'&&f.status==='unknown'));assert.equal(s.driverCandidates[0].id,'driver');assert.equal(s.trace.snapshot().status,'attention');await assert.rejects(s.handle('care.export'),/CARE_SCAN_REQUIRED/);
});
test('cancelling during shared Windows evidence skips WUA and preserves the last completed snapshot',async t=>{
 let notifyCare;const enteredCare=new Promise(resolve=>notifyCare=resolve);const calls=[];const s=await service(t,async(script,action,payload,elevated,{signal})=>{calls.push(action);if(action==='diagnostics')return {devices:[]};if(action==='care'){notifyCare();return new Promise((resolve,reject)=>signal.addEventListener('abort',()=>reject(Error('SCAN_CANCELLED')),{once:true}));}return [];});
 const previous={id:'previous',care:localEvidence()};s.diagnostics.report=previous;s.latestCare=previous.care;s.driverCandidates=[{id:'previous'}];const pending=s.handle('diagnostics.scan',{online:true});await enteredCare;assert.equal((await s.handle('diagnostics.cancel')).cancelled,true);await assert.rejects(pending,/SCAN_CANCELLED/);assert.deepEqual(calls,['diagnostics','care']);assert.equal(s.diagnostics.report,previous);assert.equal(s.latestCare,previous.care);assert.equal(s.driverCandidates[0].id,'previous');assert.equal(s.trace.snapshot().status,'cancelled');
});
test('restart indicators are informative, incomplete providers unknown and historical events never active faults',()=>{
 const findings=careFindings(localEvidence());assert.deepEqual(findings.map(f=>[f.reason,f.status]),[['windowsRestartUnknown','unknown'],['windowsRestartPending','info'],['windowsProviderUnavailable','unknown']]);
});
