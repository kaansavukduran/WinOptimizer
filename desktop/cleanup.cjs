const fs=require('node:fs/promises');
const path=require('node:path');
const crypto=require('node:crypto');
const {atomicWrite}=require('./settings.cjs');
const inside=(root,file)=>{const rel=path.relative(root,file);return rel!==''&&!rel.startsWith('..'+path.sep)&&rel!=='..'&&!path.isAbsolute(rel);};
async function regularFile(root,file){
  if(!inside(root,file))return false;
  try{const actual=await fs.realpath(root); if(actual!==path.resolve(root))return false;
    let cursor=file;while(cursor!==root){const s=await fs.lstat(cursor);if(s.isSymbolicLink())return false;cursor=path.dirname(cursor);}
    const s=await fs.lstat(file);return s.isFile();}catch{return false;}
}
function rootsFor(local){return [{id:'temp',path:path.join(local,'Temp'),days:7},{id:'chrome',path:path.join(local,'Google','Chrome','User Data','Default','Cache','Cache_Data'),days:7},{id:'edge',path:path.join(local,'Microsoft','Edge','User Data','Default','Cache','Cache_Data'),days:7}];}
class Cleanup {
  constructor(dir,roots){this.dir=dir;this.roots=roots;this.plan=null;}
  async scan(){const files=[];const groups=[];for(const root of this.roots){let bytes=0,count=0;const pending=[root.path];
    while(pending.length&&files.length<10000){const current=pending.pop();let entries;try{const s=await fs.lstat(current);if(s.isSymbolicLink())continue;entries=await fs.readdir(current,{withFileTypes:true});}catch{continue;}
      for(const ent of entries){const file=path.join(current,ent.name);if(ent.isSymbolicLink()||!inside(root.path,file))continue;if(ent.isDirectory()){pending.push(file);continue;}
        if(!ent.isFile()||!(await regularFile(root.path,file)))continue;
        let s;try{s=await fs.stat(file);}catch{continue;}if(s.mtimeMs>Date.now()-root.days*86400000)continue;
        files.push({root:root.id,path:file,size:s.size,mtime:s.mtimeMs});bytes+=s.size;count++;if(files.length>=10000)break;}}
    groups.push({id:root.id,bytes,count});}
    this.plan={id:crypto.randomUUID(),created:Date.now(),files};return {id:this.plan.id,groups,bytes:files.reduce((a,x)=>a+x.size,0),count:files.length,capped:files.length>=10000,samples:files.slice(0,50).map(x=>({group:x.root,name:path.basename(x.path),path:x.path,bytes:x.size}))};}
  async quarantine(planId,selected){
    if(!this.plan||this.plan.id!==planId||Date.now()-this.plan.created>30*60000)throw Error('SCAN_EXPIRED');
    const plan=this.plan;this.plan=null;const id=crypto.randomUUID();const dest=path.join(this.dir,'quarantine',id);await fs.mkdir(dest,{recursive:true});
    const journal={id,type:'cleanup',at:new Date().toISOString(),status:'pending',items:[],bytes:0,skipped:0};const journalFile=path.join(dest,'journal.json');atomicWrite(journalFile,journal);
    for(const f of plan.files.filter(f=>selected.includes(f.root))){const root=this.roots.find(r=>r.id===f.root);if(!root||!(await regularFile(root.path,f.path))){journal.skipped++;continue;}
      let stat;try{stat=await fs.stat(f.path);}catch{journal.skipped++;continue;}if(stat.size!==f.size||stat.mtimeMs!==f.mtime){journal.skipped++;continue;}
      const target=path.join(dest,String(journal.items.length));const entry={original:f.path,saved:target,root:f.root,size:f.size,moved:false};journal.items.push(entry);atomicWrite(journalFile,journal);
      try{await fs.rename(f.path,target);entry.moved=true;journal.bytes+=f.size;}catch{journal.skipped++;}atomicWrite(journalFile,journal);}
    journal.status='complete';atomicWrite(journalFile,journal);return journal;
  }
  async journals(){let ids;try{ids=await fs.readdir(path.join(this.dir,'quarantine'));}catch{return [];}
    const result=[];for(const id of ids){if(!/^[a-f0-9-]{36}$/.test(id))continue;try{const j=JSON.parse(await fs.readFile(path.join(this.dir,'quarantine',id,'journal.json'),'utf8'));result.push(j);}catch{}}
    return result.sort((a,b)=>b.at.localeCompare(a.at));}
  async restore(id){const j=(await this.journals()).find(x=>x.id===id);if(!j||['purged','restored'].includes(j.status))throw Error('BACKUP_UNAVAILABLE');
    const base=path.join(this.dir,'quarantine',id);let restored=0,conflicts=0;
    for(const f of j.items.filter(x=>x.moved&&!x.restored&&!x.purged)){
      const root=this.roots.find(x=>x.id===f.root);if(!root||!inside(root.path,f.original)||!inside(base,f.saved)||!(await regularFile(base,f.saved))){conflicts++;continue;}
      try{const parent=await fs.realpath(path.dirname(f.original));if(parent!==path.resolve(path.dirname(f.original)))throw Error();
        // COPYFILE_EXCL never overwrites a newly created file at the original path.
        await fs.copyFile(f.saved,f.original,require('node:fs').constants.COPYFILE_EXCL);await fs.unlink(f.saved);f.restored=true;restored++;
      }catch{conflicts++;}atomicWrite(path.join(base,'journal.json'),j);}
    j.status=conflicts?'partial':'restored';atomicWrite(path.join(base,'journal.json'),j);return {restored,conflicts};}
  async purge(id){const j=(await this.journals()).find(x=>x.id===id);if(!j||j.status==='purged')throw Error('BACKUP_UNAVAILABLE');const base=path.join(this.dir,'quarantine',id);let bytes=0,failed=0;
    for(const f of j.items.filter(x=>x.moved&&!x.restored&&!x.purged)){if(!inside(base,f.saved)||!(await regularFile(base,f.saved))){failed++;continue;}try{await fs.unlink(f.saved);f.purged=true;bytes+=f.size;}catch{failed++;}atomicWrite(path.join(base,'journal.json'),j);}
    j.status=failed?'partial':'purged';atomicWrite(path.join(base,'journal.json'),j);return {bytes,failed};}
}
module.exports={Cleanup,rootsFor,inside,regularFile};
