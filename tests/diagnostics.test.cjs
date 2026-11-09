const test=require('node:test');const assert=require('node:assert/strict');
const {Diagnostics,classify,verified,TTL}=require('../desktop/diagnostics.cjs');
const inventory=()=>({devices:[{id:'ok',name:'Old but working',code:0,present:true,version:'1.0',date:'2006-01-01'},{id:'missing',name:'Missing',code:28,present:true},{id:'disabled',name:'Disabled',code:22,present:true},{id:'unplugged',name:'Unplugged',code:45,present:false},{id:'unknown',code:null}],audio:[{id:'Audiosrv',status:'Stopped',startType:'Automatic'},{id:'AudioEndpointBuilder',status:'Stopped',startType:'Disabled'}],network:{adapters:[{status:'Up'}],dnsChecked:true,dnsOk:false},display:[],runtimes:[{id:'vc-x86',installed:false}],unavailable:[]});
test('scan distinguishes actual faults, disabled and unplugged devices, optional runtimes and update offers',()=>{
 const findings=classify(inventory(),[{id:'update',name:'Driver offered'}]);
 assert.deepEqual(findings.filter(f=>f.status==='issue').map(f=>f.id),['device:missing','audio:Audiosrv','network:dns']);
 assert.equal(findings.find(f=>f.id==='device:disabled').status,'info');assert.ok(!findings.some(f=>f.id==='device:unplugged'));
 assert.equal(findings.find(f=>f.id==='device:unknown').status,'unknown');assert.equal(findings.find(f=>f.id==='runtime:vc-x86').status,'optional');
 assert.equal(findings.find(f=>f.id==='update:update').status,'update');assert.equal(findings.find(f=>f.id==='devices:summary').evidence.disconnected,1);
});
test('failed providers and failed online update queries are not reported healthy or no updates',()=>{
 const findings=classify({...inventory(),unavailable:['devices','audio']},null,true);
 assert.ok(!findings.some(f=>f.reason==='deviceSummary'||f.reason==='audioRunning'||f.reason==='noUpdates'));
 assert.equal(findings.find(f=>f.id==='updates:unknown').status,'unknown');
});
function fixture({after,fail=false}={}){
 const calls=[],events=[];let reads=0;
 const manager=new Diagnostics(async(action,payload,elevated)=>{calls.push({action,payload,elevated});if(action==='diagnostics'){reads++;return reads>=3&&after?after:inventory();}if(action==='diagnostic-repair'&&fail)throw Error('WINDOWS_FAILED');return {completed:true};},(type,data)=>{const event={type,...data};events.push(event);return event;});
 return {manager,calls,events};
}
test('repair requires a fresh exact report, confirmation and an action offered by that finding',async()=>{
 const {manager,calls}=fixture();const report=await manager.scan();
 for(const payload of [{},{confirm:true,reportId:'forged'},{confirm:true,reportId:report.id,findingId:'audio:AudioEndpointBuilder',actionId:'audio-start'},{confirm:true,reportId:report.id,findingId:'device:missing',actionId:'run-script'}])await assert.rejects(manager.repair(payload));
 assert.ok(!calls.some(c=>c.action==='diagnostic-repair'));
 manager.created-=TTL+1;await assert.rejects(manager.repair({confirm:true,reportId:report.id,findingId:'audio:Audiosrv',actionId:'audio-start'}),/SCAN_EXPIRED/);
});
test('repair rechecks, uses fixed native actions, verifies the result and consumes the original report',async()=>{
 const after=inventory();after.audio[0].status='Running';const {manager,calls,events}=fixture({after});const report=await manager.scan();
 const payload={reportId:report.id,findingId:'audio:Audiosrv',actionId:'audio-start',confirm:true,target:'ArbitraryService'};
 const result=await manager.repair(payload);assert.equal(result.success,true);assert.equal(result.status,'fixed');assert.notEqual(result.report.id,report.id);
 assert.deepEqual(calls.find(c=>c.action==='diagnostic-repair'),{action:'diagnostic-repair',payload:{kind:'audio-start',target:'Audiosrv'},elevated:true});assert.equal(events[0].status,'fixed');
 await assert.rejects(manager.repair(payload),/SCAN_EXPIRED/);
});
test('running a command is not proof of repair; missing postcheck data remains unverified',async()=>{
 const first=fixture();const report=await first.manager.scan();const result=await first.manager.repair({reportId:report.id,findingId:'device:missing',actionId:'device-rescan',confirm:true});assert.equal(result.status,'still-present');assert.equal(result.success,false);
 const after=inventory();after.devices=[];const second=fixture({after});const r=await second.manager.scan();const unknown=await second.manager.repair({reportId:r.id,findingId:'device:missing',actionId:'device-rescan',confirm:true});assert.equal(unknown.status,'unverified');assert.equal(unknown.success,false);
 assert.equal(verified({id:'network:dns',category:'network'},{network:{dnsChecked:false},unavailable:[]}),null);
});
test('a changed or intentionally disabled target is rejected before mutation',async()=>{
 let reads=0;const calls=[];const manager=new Diagnostics(async(action)=>{calls.push(action);const raw=inventory();if(++reads>1)raw.audio[0].startType='Disabled';return raw;},()=>{});const r=await manager.scan();await assert.rejects(manager.repair({confirm:true,reportId:r.id,findingId:'audio:Audiosrv',actionId:'audio-start'}),/DIAGNOSTIC_CHANGED/);assert.ok(!calls.includes('diagnostic-repair'));
});
test('online scan failure preserves local results; offline scan never calls Windows Update',async()=>{
 const calls=[];const manager=new Diagnostics(async(action)=>{calls.push(action);if(action==='windows-updates')throw Error('NETWORK_FAILED');return inventory();},()=>{});
 await manager.scan({online:false});assert.deepEqual(calls,['diagnostics']);const report=await manager.scan({online:true});assert.ok(report.findings.some(f=>f.reason==='updateUnavailable'));assert.ok(report.findings.some(f=>f.reason==='missingDriver'));
});
test('failed native repair remains in history as failed and invalidates the plan',async()=>{
 const {manager,events}=fixture({fail:true});const r=await manager.scan();const payload={reportId:r.id,findingId:'network:dns',actionId:'dns-flush',confirm:true};await assert.rejects(manager.repair(payload),/WINDOWS_FAILED/);assert.equal(events[0].status,'failed');assert.equal(manager.report,null);await assert.rejects(manager.repair(payload),/SCAN_EXPIRED/);
});

test('cancelling a read-only scan aborts its native process and leaves previous results intact',async()=>{const manager=new Diagnostics(async(_action,_payload,_elevated,{signal})=>new Promise((_resolve,reject)=>signal.addEventListener('abort',()=>reject(Error('SCAN_CANCELLED')),{once:true})),()=>({}));manager.report={id:'previous'};const pending=manager.scan();assert.equal(manager.cancel().cancelled,true);await assert.rejects(pending,/SCAN_CANCELLED/);assert.equal(manager.report.id,'previous');assert.equal(manager.cancel().cancelled,false);});
