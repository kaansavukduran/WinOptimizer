const fs=require('node:fs');const fsp=require('node:fs/promises');const path=require('node:path');const crypto=require('node:crypto');
const {Packages}=require('./packages.cjs');const {Runtimes}=require('./runtime.cjs');
const {Diagnostics}=require('./diagnostics.cjs');
const {Settings,atomicWrite}=require('./settings.cjs');const {Cleanup,rootsFor}=require('./cleanup.cjs');const windows=require('./windows.cjs');
class Service {
  constructor({dir,local,locale='tr',backend,version,platform=process.platform,run=windows.run,roots}){
    this.dir=dir;this.backend=backend;this.version=version;this.platform=platform;this.run=run;const fresh=!fs.existsSync(path.join(dir,'settings.json'));this.settings=new Settings(dir,locale);if(fresh)this.settings.data.channel=version.includes('-')?'beta':'stable';this.cleanup=new Cleanup(dir,roots||rootsFor(local));this.busy=false;this.latestHealth=null;this.driverCandidates=[];this.startup=[];this.diagnostics=new Diagnostics((...args)=>this.native(...args),(...args)=>this.record(...args),Date.now,()=>this.save(),offers=>this.availableDriverOffers(offers));this.packages=new Packages(dir,(...args)=>this.native(...args),(...args)=>this.record(...args),()=>this.save());this.operation=null;this.runtimes=new Runtimes(dir,(...args)=>this.native(...args),(...args)=>this.record(...args),status=>{this.operation=status;},undefined,()=>this.save());this.offlineDevices=[];this.ghosts=[];this.focusApps=[];this.stateFile=path.join(dir,'activity.json');
    try{this.state=JSON.parse(fs.readFileSync(this.stateFile,'utf8'));if(this.state.schema!==1||!Array.isArray(this.state.events)||!Array.isArray(this.state.milestones))throw Error();}catch{this.state={schema:1,events:[],milestones:[]};}
    if(!Array.isArray(this.state.ignoredUpdates))this.state.ignoredUpdates=[];
  }
  record(type,data){const event={...data,targetId:data?.id??data?.targetId,id:crypto.randomUUID(),at:new Date().toISOString(),type};this.state.events.unshift(event);this.state.events=this.state.events.slice(0,500);this.save();return event;}
  save(){atomicWrite(this.stateFile,this.state);}
  milestone(id){if(!this.state.milestones.includes(id)){this.state.milestones.push(id);this.save();}}
  async native(action,payload={},elevated=false,options={}){if(this.platform!=='win32')throw Error('WINDOWS_ONLY');return this.run(this.backend,action,payload,elevated,options);}
  availableDriverOffers(offers){return (offers||[]).filter(c=>!/^firmware$/i.test(String(c.driverClass||''))&&!this.state.ignoredUpdates.some(e=>e.id===c.id));}
  async installDriverUpdates(ids){
    if(!Array.isArray(ids)||!ids.length||ids.length>10000||new Set(ids).size!==ids.length||ids.some(id=>!this.availableDriverOffers(this.driverCandidates).some(c=>c.id===id)))throw Error('INVALID_SELECTION');
    // Large selections use a hash-pinned plan to stay below the Windows/UAC command-line limit.
    const payload={backupDestination:path.join(this.dir,'DriverBackups',crypto.randomUUID())};let idsFile;
    try {
      if(ids.length>20){idsFile=path.join(this.dir,'Plans',crypto.randomUUID()+'.json');fs.mkdirSync(path.dirname(idsFile),{recursive:true});const data=Buffer.from(JSON.stringify({ids}));fs.writeFileSync(idsFile,data,{mode:0o600,flag:'wx'});payload.idsFile=idsFile;payload.idsSha256=crypto.createHash('sha256').update(data).digest('hex');}
      else payload.ids=ids;
      const result=await this.native('windows-install',payload,true);this.record('windows-install',result);this.driverCandidates=[];return result;
    }finally{if(idsFile)fs.rmSync(idsFile,{force:true});}
  }
  async handle(command,payload={}){
    if(command==='diagnostics.cancel')return this.diagnostics.cancel();
    if(command==='operation.status')return this.operation;
    if(command==='bootstrap')return {version:this.version,platform:this.platform,settings:this.settings.data,milestones:this.state.milestones,warning:this.settings.warning};
    if(command==='settings.save')return this.settings.save(payload);
    if(command==='history')return {events:this.state.events,cleanup:await this.cleanup.journals(),milestones:this.state.milestones};
    if(this.busy)throw Error('OPERATION_BUSY');this.busy=true;
    try{switch(command){
      case 'workshop.library':return {packages:await this.packages.library(),ignored:this.state.ignoredUpdates,focus:this.state.focus||null};
      case 'package.inspect':return await this.packages.inspect(payload.id);
      case 'package.import':return await this.packages.importFolder(payload.directory);
      case 'package.apply':return await this.packages.apply(payload);
      case 'runtime.prepare':return await this.runtimes.prepare(payload);
      case 'runtime.install':return await this.runtimes.install(payload);
      case 'runtime.inventory':{const result=await this.native('diagnostics');return result.unavailable?.includes('runtimes')?{available:false,items:[]}:{available:true,items:result.runtimes};}
      case 'restore-points':return await this.native(command);
      case 'restore-point-create':{if(payload.confirm!==true)throw Error('CONFIRM_REQUIRED');const r=await this.native(command,{},true);this.record(command,r);return r;}
      case 'offline.inventory':{const r=await this.native('diagnostics');if(r.unavailable?.includes('devices'))throw Error('WINDOWS_FAILED');this.offlineDevices=r.devices.filter(d=>d.present!==false);return {created:new Date().toISOString(),devices:this.offlineDevices};}
      case 'ghosts':this.ghosts=await this.native(command)||[];return this.ghosts;
      case 'ghost-remove':{if(payload.confirm!==true||!this.ghosts.some(d=>d.id===payload.id))throw Error('INVALID_SELECTION');const r=await this.native(command,{id:payload.id},true);this.record(command,r);this.ghosts=[];return r;}
      case 'updates.ignore':{const entry=this.driverCandidates.find(c=>c.id===payload.id);if(!entry)throw Error('INVALID_SELECTION');if(!this.state.ignoredUpdates.some(e=>e.id===entry.id))this.state.ignoredUpdates.push({id:entry.id,name:entry.name});this.driverCandidates=this.driverCandidates.filter(c=>c.id!==entry.id);this.save();return {ignored:true};}
      case 'updates.unignore':{if(!this.state.ignoredUpdates.some(e=>e.id===payload.id))throw Error('INVALID_SELECTION');this.state.ignoredUpdates=this.state.ignoredUpdates.filter(e=>e.id!==payload.id);this.save();return {restored:true};}
      case 'focus.inventory':{this.focusApps=await this.native('focus-apps')||[];return {apps:this.focusApps,powers:await this.native('power-profiles')};}
      case 'focus-apps':this.focusApps=await this.native(command)||[];return this.focusApps;
      case 'focus.start':{
        if(payload.confirm!==true||this.state.focus||!Array.isArray(payload.ids)||payload.ids.length>30)throw Error('INVALID_SELECTION');
        const apps=payload.ids.map(id=>this.focusApps.find(a=>a.id===id));if(apps.some(a=>!a))throw Error('INVALID_SELECTION');
        const plans=await this.native('power-profiles');const previous=plans.find(p=>p.active),target=plans.find(p=>p.id===payload.powerId);if(!previous||!target)throw Error('POWER_UNAVAILABLE');
        this.state.focus={id:crypto.randomUUID(),previous:previous.id,applied:target.id,at:new Date().toISOString(),status:'pending'};this.save();
        try{await this.native('power-set',{id:target.id});this.state.focus.status='active';this.save();const r=await this.native('focus-close',{apps});this.record('focus.start',{...this.state.focus,...r});return {...r,focus:this.state.focus};}catch(e){this.save();throw e;}
      }
      case 'focus.stop':{
        const session=this.state.focus;if(!session||payload.confirm!==true)throw Error('INVALID_SELECTION');const plans=await this.native('power-profiles');const active=plans.find(p=>p.active);
        if(active?.id!==session.applied){this.state.focus=null;this.save();return {success:false,conflict:true};}
        const r=await this.native('power-set',{id:session.previous});this.state.focus=null;this.record('focus.stop',r);return {success:true};
      }
      case 'diagnostics.scan':{const report=await this.diagnostics.scan(payload);this.driverCandidates=this.diagnostics.updates;return report;}
      case 'diagnostics.updates':{const ids=this.diagnostics.selectUpdates(payload);return await this.installDriverUpdates(ids);}
      case 'diagnostics.repair':return await this.diagnostics.repair(payload);
      case 'scan':{if(this.platform!=='win32')throw Error('WINDOWS_ONLY');const result=await this.cleanup.scan();this.milestone('scan');return result;}
      case 'cleanup':{if(!Array.isArray(payload.groups)||!payload.groups.length||!payload.groups.every(x=>['temp','chrome','edge'].includes(x)))throw Error('INVALID_SELECTION');const result=await this.cleanup.quarantine(payload.planId,payload.groups);if(result.bytes)this.record('cleanup',{backupId:result.id,bytes:result.bytes,skipped:result.skipped});return result;}
      case 'restore':{const result=await this.cleanup.restore(payload.id);this.record('restore',result);return result;}
      case 'purge':{if(payload.confirm!==true)throw Error('CONFIRM_REQUIRED');const result=await this.cleanup.purge(payload.id);this.record('purge',result);return result;}
      case 'health':{this.latestHealth=await this.native('health');this.milestone('health');return this.latestHealth;}
      case 'drivers':return await this.native('drivers');
      case 'driver-backup':{const destination=path.join(this.dir,'DriverBackups',crypto.randomUUID());const result=await this.native('driver-backup',{destination},true);if(result.packages>0){this.milestone('drivers');this.record('driver-backup',result);}return result;}
      case 'startup':this.startup=await this.native('startup')||[];return this.startup;
      case 'startup-disable':{const entry=this.startup.find(e=>e.id===payload.id);if(!entry)throw Error('STARTUP_CHANGED');
        // Persist the original value BEFORE registry modification, including interrupted operations.
        const event=this.record('startup-disable',{entry,status:'pending'});try{const result=await this.native(command,entry);event.status='complete';this.save();return result;}catch(e){event.status='failed';this.save();throw e;}}
      case 'startup-restore':{const event=this.state.events.find(e=>e.id===payload.id&&e.type==='startup-disable'&&e.status!=='restored');if(!event)throw Error('BACKUP_UNAVAILABLE');const result=await this.native(command,event.entry);event.status='restored';this.save();return result;}
      case 'windows-updates':this.driverCandidates=this.availableDriverOffers(await this.native(command));return this.driverCandidates;
      case 'windows-install':{if(payload.confirm!==true)throw Error('INVALID_SELECTION');return await this.installDriverUpdates(payload.ids);}
      case 'network':case 'power-profiles':return await this.native(command);
      case 'dns-flush':{const result=await this.native(command);this.record(command,result);return result;}
      case 'power-set':{const result=await this.native(command,payload);this.record(command,result);return result;}
      default:throw Error('UNKNOWN_COMMAND');
    }}finally{this.busy=false;this.operation=null;}
  }
  exportData(){return {app:'WinOptimizer Aion',schema:1,version:this.version,exported:new Date().toISOString(),settings:this.settings.data,activity:this.state};}
  importData(input){if(input.app!=='WinOptimizer Aion'||input.schema!==1||!input.settings)throw Error('BACKUP_INVALID');
    // Import appearance only: never trust machine-specific rollback commands or paths from a file.
    const before=this.exportData();atomicWrite(path.join(this.dir,`before-import-${Date.now()}.json`),before);return this.settings.save(input.settings);}
}
module.exports={Service};
