// Headless Node/PowerShell business layer. No Electron or browser runtime is imported.
const fs=require('node:fs');const path=require('node:path');const readline=require('node:readline');const {spawn}=require('node:child_process');
const {Service}=require('./service.cjs');const {Updater,REPO}=require('./updater.cjs');
const args=process.argv.slice(2),option=k=>args[args.indexOf(k)+1],dir=option('--data'),portable=args.includes('--portable');if(!dir||!path.isAbsolute(dir))throw Error('INVALID_DESTINATION');
const root=path.resolve(__dirname,'..'),version=require('../package.json').version;
const service=new Service({dir,local:process.env.LOCALAPPDATA||dir,locale:option('--locale')||'tr',backend:path.join(root,'backend','Windows.ps1'),version});
const updater=new Updater(path.join(dir,'Updates'),fs.readFileSync(path.join(__dirname,'update-public-key.pem')),version);
const sources={'oem-nvidia':'https://www.nvidia.com/en-us/drivers/','oem-amd':'https://www.amd.com/en/support/download/drivers.html','oem-intel':'https://www.intel.com/content/www/us/en/download-center/home.html','runtime-license':'https://aka.ms/VCRedistLicense',github:`https://github.com/${REPO}`,releases:`https://github.com/${REPO}/releases`,windows:'ms-settings:windowsupdate',security:'windowsdefender:',startup:'ms-settings:startupapps',sound:'ms-settings:sound',display:'ms-settings:display','network-settings':'ms-settings:network-status',devices:'ms-settings:troubleshoot','visual-cpp':'https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170',directx:'https://www.microsoft.com/en-us/download/details.aspx?id=35',game:'ms-settings:gaming-gamemode'};
async function tracedUpdate(command,operation){
 if(service.busy)throw Error('OPERATION_BUSY');service.busy=true;service.trace.start(command);service.trace.add({step:'update-network',status:'running'});
 try{const value=await operation();service.trace.add({step:'update-network',status:'complete'});service.trace.finish(value);return value;}catch(error){service.trace.finish(null,error);throw error;}finally{service.busy=false;service.operation=null;}
}
async function invoke(command,p={}){
 if(command==='bootstrap')return {...await service.handle(command),portable,engine:'Qt Widgets',dataDirectory:dir};
 if(command==='external'){if(!Object.hasOwn(sources,p.id))throw Error('INVALID_SELECTION');return {url:sources[p.id]};}
 if(command==='folder.open'){const folders={data:dir,drivers:path.join(dir,'DriverBackups')};if(!folders[p.id])throw Error('INVALID_SELECTION');fs.mkdirSync(folders[p.id],{recursive:true});return {folder:folders[p.id]};}
 if(command==='report.export')return {app:'WinOptimizer Aion',version,created:new Date().toISOString(),health:service.latestHealth,hardware:service.latestHardware,diagnostics:service.diagnostics.report,activity:service.state,operation:service.trace.snapshot()};
 if(command==='hardware.export'){if(!service.latestHardware)throw Error('HARDWARE_SCAN_REQUIRED');return {app:'WinOptimizer Aion',version,...service.latestHardware};}
 if(command==='backup.export')return service.exportData();
 if(command==='backup.import')return service.importData(p);
 if(command==='updates.check')return tracedUpdate(command,()=>updater.check(service.settings.data.channel));
 if(command==='updates.portable'){if(!portable||!updater.pending?.portable)throw Error('UPDATE_CHECK_FIRST');return {url:updater.pending.portable.url};}
 if(command==='updates.install'){if(portable)throw Error('PORTABLE_MANUAL_UPDATE');if(p.confirm!==true)throw Error('CONFIRM_REQUIRED');return tracedUpdate(command,async()=>{const file=await updater.download();service.settings.save(service.settings.data);service.save();return {installer:file};});}
 if(command==='offline.export')return {app:'WinOptimizer Aion',schema:1,...await service.handle('offline.inventory')};
 if(command==='hardware.search'){const d=service.offlineDevices.find(d=>d.id===p.id),h=d?.hardwareIds?.find(h=>typeof h==='string'&&h.length>0&&h.length<=500);if(!h)throw Error('INVALID_SELECTION');return {url:'https://www.catalog.update.microsoft.com/Search.aspx?q='+encodeURIComponent(h)};}
 if(command==='system.open'){const names={restore:'rstrui.exe',protection:'SystemPropertiesProtection.exe',devices:'devmgmt.msc'};if(!Object.hasOwn(names,p.id))throw Error('INVALID_SELECTION');const folder=path.join(process.env.SystemRoot||'C:\\Windows','System32'),exe=path.join(folder,p.id==='devices'?'mmc.exe':names[p.id]),child=spawn(exe,p.id==='devices'?[path.join(folder,names[p.id])]:[],{detached:true,stdio:'ignore',windowsHide:false});await new Promise((resolve,reject)=>{child.once('spawn',resolve);child.once('error',reject);});child.unref();return {opened:true};}
 return service.handle(command,p);
}
const input=readline.createInterface({input:process.stdin,crlfDelay:Infinity});
input.on('line',line=>{if(line.length>8*1024*1024)return;let request;try{request=JSON.parse(line);if(!Number.isSafeInteger(request.id)||typeof request.command!=='string')throw Error();}catch{return;}
 Promise.resolve().then(()=>invoke(request.command,request.payload)).then(data=>process.stdout.write(JSON.stringify({id:request.id,ok:true,data})+'\n'),error=>process.stdout.write(JSON.stringify({id:request.id,ok:false,error:/^[A-Z][A-Z0-9_]+$/.test(error.message)?error.message:'OPERATION_FAILED'})+'\n'));
});input.on('close',()=>process.exit(0));
