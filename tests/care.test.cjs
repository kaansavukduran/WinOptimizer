const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs/promises'),os=require('node:os'),path=require('node:path');
const {Service}=require('../desktop/service.cjs');const {reducedCare,reducedComponent}=require('../desktop/care.cjs');
async function service(t,run){const dir=await fs.mkdtemp(path.join(os.tmpdir(),'aion-care-'));t.after(()=>fs.rm(dir,{recursive:true,force:true}));return new Service({dir,local:dir,version:'6.3.0',platform:'win32',backend:'fixture.ps1',run});}
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
