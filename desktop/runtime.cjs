const fs=require('node:fs/promises');const path=require('node:path');const crypto=require('node:crypto');
const CATALOG=Object.freeze({
 'vc-x64':{url:'https://aka.ms/vc14/vc_redist.x64.exe',file:'vc_redist.x64.exe'},
 'vc-x86':{url:'https://aka.ms/vc14/vc_redist.x86.exe',file:'vc_redist.x86.exe'},
 'directx-legacy':{url:'https://download.microsoft.com/download/8/4/a/84a35bf1-dafe-4ae8-82af-ad2ae20b6b14/directx_Jun2010_redist.exe',file:'directx_Jun2010_redist.exe'}
});
const MAX_BYTES=128*1024*1024;
function allowed(url){const u=new URL(url);return u.protocol==='https:'&&!u.username&&!u.password&&['aka.ms','download.microsoft.com','download.visualstudio.microsoft.com'].includes(u.hostname)&&(!u.port||u.port==='443');}
async function download(url,destination,progress=()=>{},fetcher=fetch){
 const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),300000);let handle;
 try{
  let response;for(let n=0;n<7;n++){
   if(!allowed(url))throw Error('RUNTIME_SOURCE_INVALID');response=await fetcher(url,{redirect:'manual',signal:controller.signal});
   if([301,302,303,307,308].includes(response.status)){const location=response.headers.get('location');await response.body?.cancel();if(!location)throw Error('RUNTIME_DOWNLOAD_FAILED');url=new URL(location,url).href;continue;}break;
  }
  if(!response?.ok||!response.body)throw Error('RUNTIME_DOWNLOAD_FAILED');const total=Number(response.headers.get('content-length'))||null;if(total&&total>MAX_BYTES)throw Error('RUNTIME_DOWNLOAD_FAILED');
  handle=await fs.open(destination,'wx',0o600);const hash=crypto.createHash('sha256');let bytes=0;
  for await(const chunk of response.body){bytes+=chunk.length;if(bytes>MAX_BYTES)throw Error('RUNTIME_DOWNLOAD_FAILED');hash.update(chunk);await handle.write(chunk);progress({phase:'download',bytes,total});}
  if(bytes<10000||(total&&total!==bytes))throw Error('RUNTIME_DOWNLOAD_FAILED');return {bytes,sha256:hash.digest('hex')};
 }catch(e){await handle?.close();handle=null;await fs.rm(destination,{force:true});throw e;}finally{clearTimeout(timer);await handle?.close();}
}
class Runtimes {
 constructor(dir,native,record,progress=()=>{},downloader=download,persist=()=>{}){this.persist=persist;this.dir=dir;this.native=native;this.record=record;this.progress=progress;this.downloader=downloader;this.plans=new Map();}
 async prepare(payload){const spec=CATALOG[payload.id];if(!spec)throw Error('INVALID_SELECTION');const id=crypto.randomUUID(),directory=path.join(this.dir,'Runtimes',id);await fs.mkdir(directory,{recursive:true});const file=path.join(directory,spec.file);
  try{const result=await this.downloader(spec.url,file,this.progress);this.progress({phase:'verify'});const verification=await this.native('runtime-verify',{id:payload.id,file,sha256:result.sha256});if(!verification.valid)throw Error('RUNTIME_SIGNATURE_INVALID');const plan={id,kind:payload.id,file,...result,at:Date.now()};this.plans.set(id,plan);return {id,kind:plan.kind,bytes:plan.bytes,sha256:plan.sha256,publisher:verification.publisher};}catch(e){await fs.rm(directory,{recursive:true,force:true});throw e;}
 }
 async install(payload){if(payload.confirm!==true||payload.acceptLicense!==true)throw Error('CONFIRM_REQUIRED');const p=this.plans.get(payload.planId);if(!p||Date.now()-p.at>60*60*1000)throw Error('SCAN_EXPIRED');this.plans.delete(p.id);
  this.progress({phase:'install'});const event=this.record('runtime-install',{kind:p.kind,status:'pending',success:false});
  try{const result=await this.native('runtime-install',{id:p.kind,file:p.file,sha256:p.sha256},true);Object.assign(event,result,{status:result.success?'complete':'failed'});this.persist();return result;}catch(e){event.status='failed';this.persist();throw e;}finally{await fs.rm(path.dirname(p.file),{recursive:true,force:true});}
 }
}
module.exports={Runtimes,CATALOG,download,allowed,MAX_BYTES};
