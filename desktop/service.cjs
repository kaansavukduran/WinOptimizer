const fs=require('node:fs');const fsp=require('node:fs/promises');const path=require('node:path');const crypto=require('node:crypto');
const {Settings,atomicWrite}=require('./settings.cjs');const {Cleanup,rootsFor}=require('./cleanup.cjs');const windows=require('./windows.cjs');
class Service {
  constructor({dir,local,locale='tr',backend,version,platform=process.platform,run=windows.run,roots}){
    this.dir=dir;this.backend=backend;this.version=version;this.platform=platform;this.run=run;this.settings=new Settings(dir,locale);this.cleanup=new Cleanup(dir,roots||rootsFor(local));this.busy=false;this.latestHealth=null;this.driverCandidates=[];this.startup=[];this.stateFile=path.join(dir,'activity.json');
    try{this.state=JSON.parse(fs.readFileSync(this.stateFile,'utf8'));if(this.state.schema!==1||!Array.isArray(this.state.events)||!Array.isArray(this.state.milestones))throw Error();}catch{this.state={schema:1,events:[],milestones:[]};}
  }
  record(type,data){const event={id:crypto.randomUUID(),at:new Date().toISOString(),type,...data};this.state.events.unshift(event);this.state.events=this.state.events.slice(0,500);this.save();return event;}
  save(){atomicWrite(this.stateFile,this.state);}
  milestone(id){if(!this.state.milestones.includes(id)){this.state.milestones.push(id);this.save();}}
  async native(action,payload={},elevated=false){if(this.platform!=='win32')throw Error('WINDOWS_ONLY');return this.run(this.backend,action,payload,elevated);}
  async handle(command,payload={}){
    if(command==='bootstrap')return {version:this.version,platform:this.platform,settings:this.settings.data,milestones:this.state.milestones,warning:this.settings.warning};
    if(command==='settings.save')return this.settings.save(payload);
    if(command==='history')return {events:this.state.events,cleanup:await this.cleanup.journals(),milestones:this.state.milestones};
    if(this.busy)throw Error('OPERATION_BUSY');this.busy=true;
    try{switch(command){
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
      case 'windows-updates':this.driverCandidates=await this.native(command)||[];return this.driverCandidates;
      case 'windows-install':{if(payload.confirm!==true||!Array.isArray(payload.ids)||!payload.ids.length||payload.ids.some(id=>!this.driverCandidates.some(c=>c.id===id)))throw Error('INVALID_SELECTION');const result=await this.native(command,{ids:payload.ids},true);this.record('windows-install',result);this.driverCandidates=[];return result;}
      case 'network':case 'power-profiles':return await this.native(command);
      case 'dns-flush':{const result=await this.native(command);this.record(command,result);return result;}
      case 'power-set':{const result=await this.native(command,payload);this.record(command,result);return result;}
      default:throw Error('UNKNOWN_COMMAND');
    }}finally{this.busy=false;}
  }
  exportData(){return {app:'WinOptimizer Aion',schema:1,version:this.version,exported:new Date().toISOString(),settings:this.settings.data,activity:this.state};}
  importData(input){if(input.app!=='WinOptimizer Aion'||input.schema!==1||!input.settings)throw Error('BACKUP_INVALID');
    // Import appearance only: never trust machine-specific rollback commands or paths from a file.
    const before=this.exportData();atomicWrite(path.join(this.dir,`before-import-${Date.now()}.json`),before);return this.settings.save(input.settings);}
}
module.exports={Service};
