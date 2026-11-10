const {execFile,spawn}=require('node:child_process');
const path=require('node:path');const fs=require('node:fs/promises');const os=require('node:os');
const ACTIONS=new Set(['hardware','focus-apps','focus-close','package-inspect','package-apply','runtime-verify','runtime-install','restore-points','restore-point-create','ghosts','ghost-remove','diagnostics','diagnostic-repair','health','drivers','driver-backup','startup','startup-disable','startup-restore','windows-updates','windows-install','network','dns-flush','power-profiles','power-set']);
function command(script,action,payload){if(!ACTIONS.has(action))throw Error('UNKNOWN_COMMAND');return ['-NoLogo','-NoProfile','-NonInteractive','-ExecutionPolicy','Bypass','-File',script,'-Action',action,'-PayloadBase64',Buffer.from(JSON.stringify(payload||{})).toString('base64')];}
function parse(stdout){const value=JSON.parse(stdout.replace(/^\uFEFF/,''));if(!value.ok)throw Error(value.error||'WINDOWS_FAILED');return value.data;}
function environment(exe){
  const inherited=(process.env.PSModulePath||'').split(';').filter(p=>p&&!/[\\/]PowerShell[\\/](?:6|7)(?:[\\/]|$)/i.test(p));
  return {...process.env,PSModulePath:[path.join(path.dirname(exe),'Modules'),path.join(process.env.ProgramFiles||'C:\\Program Files','WindowsPowerShell','Modules'),...inherited].join(';')};
}
async function run(script,action,payload={},elevated=false,options={}){
 if(options.onProgress){const dir=await fs.mkdtemp(path.join(os.tmpdir(),'aion-progress-')),progressFile=path.join(dir,'progress.jsonl'),stop=require('./progress.cjs').watchProgress(progressFile,options.onProgress);try{return await run(script,action,payload,elevated,{...options,onProgress:null,progressFile});}finally{await stop();await fs.rm(dir,{recursive:true,force:true});}}
  if(process.platform!=='win32')return Promise.reject(Error('WINDOWS_ONLY'));
  const exe=path.join(process.env.SystemRoot||'C:\\Windows','System32','WindowsPowerShell','v1.0','powershell.exe');
  if(elevated)return elevate(exe,script,action,payload,options);
  return new Promise((resolve,reject)=>{execFile(exe,[...command(script,action,payload),...(options.progressFile?['-ProgressFile',options.progressFile]:[])],{env:environment(exe),signal:options.signal,windowsHide:true,maxBuffer:20*1024*1024,timeout:['windows-updates','hardware'].includes(action)?240000:120000,encoding:'utf8'},(error,stdout)=>{if(error?.name==='AbortError')return reject(Error('SCAN_CANCELLED'));if(error)return reject(Error(error.killed?'OPERATION_TIMEOUT':'WINDOWS_FAILED'));try{resolve(parse(stdout));}catch(e){reject(e);}});});
}
async function elevate(exe,script,action,payload,options={}){
  const dir=await fs.mkdtemp(path.join(os.tmpdir(),'aion-uac-'));const result=path.join(dir,'result.json');const args=[...command(script,action,payload),'-ResultFile',result,...(options.progressFile?['-ProgressFile',options.progressFile]:[])];
  const quoted=args.map(a=>'"'+a.replace(/"/g,'')+'"').join(' ');
  const ps=`$ErrorActionPreference='Stop'; try { $p=Start-Process -FilePath '${exe.replace(/'/g,"''")}' -ArgumentList '${quoted.replace(/'/g,"''")}' -Verb RunAs -Wait -PassThru; exit $p.ExitCode } catch { exit 1223 }`;
  try{await new Promise((resolve,reject)=>{const p=spawn(exe,['-NoProfile','-NonInteractive','-EncodedCommand',Buffer.from(ps,'utf16le').toString('base64')],{env:environment(exe),windowsHide:true});p.on('error',()=>reject(Error('WINDOWS_FAILED')));p.on('exit',code=>code===0?resolve():reject(Error('ADMIN_CANCELLED')));});return parse(await fs.readFile(result,'utf8'));}finally{await fs.rm(dir,{recursive:true,force:true});}
}
module.exports={run,command,ACTIONS,environment};
