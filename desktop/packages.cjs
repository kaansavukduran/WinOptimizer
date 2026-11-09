const fs=require('node:fs/promises');const path=require('node:path');const crypto=require('node:crypto');
const {atomicWrite}=require('./settings.cjs');
const MAX_BYTES=1024*1024*1024,MAX_FILES=6000;
async function inventory(directory){
 const root=path.resolve(directory);const list=[];let bytes=0;
 async function walk(folder){const stat=await fs.lstat(folder);if(stat.isSymbolicLink()||!stat.isDirectory())throw Error('PACKAGE_LINK');
  for(const entry of await fs.readdir(folder,{withFileTypes:true})){
   const file=path.join(folder,entry.name),s=await fs.lstat(file);if(s.isSymbolicLink())throw Error('PACKAGE_LINK');
   if(s.isDirectory()){await walk(file);continue;}if(!s.isFile())throw Error('PACKAGE_INVALID');
   if(entry.name.toLowerCase()==='backup.json'||entry.name.toLowerCase()==='package-receipt.json')continue;
   bytes+=s.size;if(bytes>MAX_BYTES||list.length>=MAX_FILES)throw Error('PACKAGE_TOO_LARGE');
   const hash=crypto.createHash('sha256');for await(const chunk of require('node:fs').createReadStream(file))hash.update(chunk);
   list.push({path:path.relative(root,file).split(path.sep).join('/'),sha256:hash.digest('hex'),bytes:s.size});
  }
 }
 await walk(root);list.sort((a,b)=>a.path.localeCompare(b.path));return {files:list,bytes};
}
function sameFiles(a,b){return a.length===b.length&&a.every((f,i)=>f.path===b[i].path&&f.sha256===b[i].sha256&&f.bytes===b[i].bytes);}
class Packages{
 constructor(dir,native,record,persist=()=>{}){this.persist=persist;this.dir=dir;this.native=native;this.record=record;this.plans=new Map();}
 async library(){const entries=[];for(const kind of ['DriverBackups','DriverPackages']){
  const base=path.join(this.dir,kind);const baseStat=await fs.lstat(base).catch(()=>null);if(baseStat?.isSymbolicLink())throw Error('PACKAGE_LINK');for(const e of await fs.readdir(base,{withFileTypes:true}).catch(()=>[])){
   if(!e.isDirectory()||!/^[a-z0-9-]{1,80}$/i.test(e.name))continue;
   const directory=path.join(base,e.name),s=await fs.lstat(directory);if(s.isSymbolicLink())continue;
   entries.push({id:kind+'/'+e.name,kind,at:s.birthtime.toISOString()});
  }
 }return entries.sort((a,b)=>b.at.localeCompare(a.at));}
 async resolve(id){const entries=await this.library();if(!entries.some(e=>e.id===id))throw Error('BACKUP_UNAVAILABLE');return path.join(this.dir,...id.split('/'));}
 async importFolder(source){
  const before=await inventory(source);if(!before.files.some(f=>/\.inf$/i.test(f.path)))throw Error('PACKAGE_INVALID');
  const id=crypto.randomUUID(),destination=path.join(this.dir,'DriverPackages',id);await fs.mkdir(destination,{recursive:true});
  try{
   for(const f of before.files){const file=path.join(destination,...f.path.split('/'));await fs.mkdir(path.dirname(file),{recursive:true});await fs.copyFile(path.join(source,...f.path.split('/')),file);}
   const after=await inventory(destination);if(!sameFiles(before.files,after.files))throw Error('PACKAGE_CHANGED');
   atomicWrite(path.join(destination,'package-receipt.json'),{created:new Date().toISOString(),...after});return await this.inspect('DriverPackages/'+id);
  }catch(e){await fs.rm(destination,{recursive:true,force:true});throw e;}
 }
 async inspect(id){
  const directory=await this.resolve(id),snapshot=await inventory(directory);const manifest=await fs.readFile(path.join(directory,'backup.json'),'utf8').then(s=>JSON.parse(s.replace(/^\uFEFF/,''))).catch(e=>{if(e.code==='ENOENT')return null;throw Error('BACKUP_INVALID');});
  if(manifest){if(!Array.isArray(manifest.files)||manifest.files.length!==snapshot.files.length||manifest.files.some(f=>!snapshot.files.some(s=>s.path.toLowerCase()===String(f.path).replaceAll('\\','/').toLowerCase()&&s.sha256.toLowerCase()===String(f.sha256).toLowerCase())))throw Error('PACKAGE_CHANGED');}
  const candidates=await this.native('package-inspect',{directory})||[];const plan={id:crypto.randomUUID(),libraryId:id,directory,files:snapshot.files,candidates,at:Date.now()};this.plans.set(plan.id,plan);
  return {id:plan.id,libraryId:id,bytes:snapshot.bytes,files:snapshot.files.length,candidates};
 }
 async apply(payload){
  if(payload.confirm!==true)throw Error('CONFIRM_REQUIRED');const p=this.plans.get(payload.planId);
  if(!p||Date.now()-p.at>30*60*1000)throw Error('SCAN_EXPIRED');
  const ids=payload.ids;if(!Array.isArray(ids)||!ids.length||ids.length>20||new Set(ids).size!==ids.length)throw Error('INVALID_SELECTION');
  const selected=ids.map(id=>p.candidates.find(c=>c.id===id&&c.eligible));if(selected.some(c=>!c))throw Error('INVALID_SELECTION');
  const now=await inventory(p.directory);if(!sameFiles(p.files,now.files))throw Error('PACKAGE_CHANGED');this.plans.delete(p.id);
  const manifestFile=path.join(this.dir,'Plans',crypto.randomUUID()+'.json');await fs.mkdir(path.dirname(manifestFile),{recursive:true});const manifestBytes=Buffer.from(JSON.stringify({files:p.files}));await fs.writeFile(manifestFile,manifestBytes,{mode:0o600});const manifestSha256=crypto.createHash('sha256').update(manifestBytes).digest('hex');
  const event=this.record('package-apply',{status:'pending',success:false,libraryId:p.libraryId,names:selected.map(c=>c.name)});
  try{const result=await this.native('package-apply',{directory:p.directory,ids,manifestFile,manifestSha256,backupDestination:path.join(this.dir,'DriverBackups',crypto.randomUUID())},true);Object.assign(event,result,{status:result.success?'complete':'partial'});this.persist();return result;}catch(e){event.status='failed';this.persist();throw e;}finally{await fs.rm(manifestFile,{force:true});}
 }
}
module.exports={Packages,inventory,sameFiles,MAX_BYTES,MAX_FILES};
