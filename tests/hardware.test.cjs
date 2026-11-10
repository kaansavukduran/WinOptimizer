const {test}=require('node:test');const assert=require('node:assert/strict');const fs=require('node:fs/promises');const path=require('node:path');const os=require('node:os');
const {Service}=require('../desktop/service.cjs');
test('hardware inventory stays local and unelevated, retains 64-bit VRAM and reports provider failures',async t=>{
 const dir=await fs.mkdtemp(path.join(os.tmpdir(),'aion-hardware-'));t.after(()=>fs.rm(dir,{recursive:true,force:true}));
 const report={schema:1,readOnly:true,online:false,success:false,sections:[{id:'gpu',status:'available',items:[{name:'Fixture GPU',dedicatedVideoBytes:12*1024**3,sharedSystemBytes:16*1024**3}]},{id:'bios',status:'unavailable',items:[]}]};
 const calls=[];const service=new Service({dir,local:dir,version:'6.1.0',platform:'win32',backend:'fixture.ps1',run:async(script,action,payload,elevated,options)=>{calls.push({action,payload,elevated});options.onProgress({step:'hardware-bios',status:'failed',reason:'provider-unavailable'});return report;}});
 const result=await service.handle('hardware',{online:true,elevated:true});
 assert.deepEqual(calls,[{action:'hardware',payload:{},elevated:false}]);assert.equal(result.sections[0].items[0].dedicatedVideoBytes,12884901888);assert.equal(service.latestHardware,result);assert.equal(service.trace.snapshot().status,'attention');assert.deepEqual(service.state.events,[]);assert.deepEqual(service.state.milestones,[]);
 const original=service.latestHardware;service.run=async()=>{throw Error('WINDOWS_FAILED')};await assert.rejects(service.handle('hardware'),/WINDOWS_FAILED/);assert.equal(service.latestHardware,original);assert.equal(service.busy,false);
});
