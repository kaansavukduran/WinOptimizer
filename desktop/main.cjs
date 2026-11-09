const {app,BrowserWindow,ipcMain,dialog,shell}=require('electron');
const path=require('node:path');const fs=require('node:fs');const fsp=require('node:fs/promises');const {spawn}=require('node:child_process');
const {Service}=require('./service.cjs');const {Updater,REPO}=require('./updater.cjs');
const local=process.env.LOCALAPPDATA||app.getPath('appData');
app.setPath('userData',path.join(local,'WinOptimizer Aion'));
if(!app.requestSingleInstanceLock()){app.quit();}else{
let window,service,updater,updating=false;const language=()=>service?.settings.data.language==='en';
const sources={'oem-nvidia':'https://www.nvidia.com/en-us/drivers/','oem-amd':'https://www.amd.com/en/support/download/drivers.html','oem-intel':'https://www.intel.com/content/www/us/en/download-center/home.html','runtime-license':'https://aka.ms/VCRedistLicense',game:'ms-settings:gaming-gamemode',github:`https://github.com/${REPO}`,releases:`https://github.com/${REPO}/releases`,windows:'ms-settings:windowsupdate',security:'windowsdefender:',startup:'ms-settings:startupapps',sound:'ms-settings:sound',display:'ms-settings:display','network-settings':'ms-settings:network-status',devices:'ms-settings:troubleshoot','visual-cpp':'https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170',directx:'https://www.microsoft.com/en-us/download/details.aspx?id=35'};
app.on('second-instance',()=>{if(window){if(window.isMinimized())window.restore();window.show();window.focus();}});
app.whenReady().then(async()=>{
  service=new Service({dir:app.getPath('userData'),local,locale:app.getLocale(),backend:path.join(app.isPackaged?process.resourcesPath:app.getAppPath(),'backend','Windows.ps1'),version:app.getVersion()});
  updater=new Updater(path.join(app.getPath('userData'),'Updates'),fs.readFileSync(path.join(__dirname,'update-public-key.pem'),'utf8'),app.getVersion());
  window=new BrowserWindow({width:1380,height:940,minWidth:440,minHeight:540,title:'WinOptimizer Aion',icon:path.join(__dirname,'../dist/assets/aion-icon.png'),backgroundColor:'#fff8fb',webPreferences:{preload:path.join(__dirname,'preload.cjs'),nodeIntegration:false,contextIsolation:true,sandbox:true,webSecurity:true}});
  window.webContents.setWindowOpenHandler(()=>({action:'deny'}));
  window.webContents.on('will-navigate',e=>e.preventDefault());
  window.webContents.session.setPermissionRequestHandler((_w,_p,callback)=>callback(false));
  ipcMain.handle('aion:command',async(event,command,payload={})=>{
    if(event.sender!==window.webContents||event.senderFrame!==window.webContents.mainFrame)return {ok:false,error:'UNAUTHORIZED'};
    try{
      if(command==='external'){if(!Object.hasOwn(sources,payload.id))throw Error('INVALID_SELECTION');await shell.openExternal(sources[payload.id]);return {ok:true,data:true};}
      if(command==='system.open'){
        const names={restore:'rstrui.exe',protection:'SystemPropertiesProtection.exe',devices:'devmgmt.msc'};if(!Object.hasOwn(names,payload.id))throw Error('INVALID_SELECTION');
        const folder=path.join(process.env.SystemRoot||'C:\\Windows','System32');const exe=payload.id==='devices'?path.join(folder,'mmc.exe'):path.join(folder,names[payload.id]);
        const args=payload.id==='devices'?[path.join(folder,'devmgmt.msc')]:[];const child=spawn(exe,args,{detached:true,stdio:'ignore',windowsHide:false});await new Promise((resolve,reject)=>{child.once('spawn',resolve);child.once('error',reject);});child.unref();return {ok:true,data:{opened:true}};
      }
      if(command==='hardware.search'){
        const device=service.offlineDevices.find(d=>d.id===payload.id);const hardware=device?.hardwareIds?.find(h=>typeof h==='string'&&h.length>0&&h.length<=500);if(!hardware)throw Error('INVALID_SELECTION');await shell.openExternal('https://www.catalog.update.microsoft.com/Search.aspx?q='+encodeURIComponent(hardware));return {ok:true,data:{opened:true}};
      }
      if(command==='offline.export'){
        const data=await service.handle('offline.inventory');const result=await dialog.showSaveDialog(window,{defaultPath:'WinOptimizer-hardware.json',filters:[{name:'JSON',extensions:['json']}]});if(result.canceled)return {ok:true,data:{cancelled:true}};await fsp.writeFile(result.filePath,JSON.stringify({app:'WinOptimizer Aion',schema:1,...data},null,2));return {ok:true,data:{saved:true}};
      }
      if(command==='package.import'){
        if(service.busy)throw Error('OPERATION_BUSY');const r=await dialog.showOpenDialog(window,{properties:['openDirectory']});if(r.canceled)return {ok:true,data:{cancelled:true}};return {ok:true,data:await service.handle(command,{directory:r.filePaths[0]})};
      }
      if(command==='folder.open'){const folders={data:service.dir,drivers:path.join(service.dir,'DriverBackups')};const dest=folders[payload.id];if(!dest)throw Error('INVALID_SELECTION');await fsp.mkdir(dest,{recursive:true});const error=await shell.openPath(dest);if(error)throw Error('FOLDER_FAILED');return {ok:true,data:true};}
      if(command==='backup.export'||command==='report.export'){
        const result=await dialog.showSaveDialog(window,{title:language()?'Export':'Dışa aktar',defaultPath:command==='backup.export'?'WinOptimizer-backup.json':'WinOptimizer-report.json',filters:[{name:'JSON',extensions:['json']}]});
        if(result.canceled)return {ok:true,data:{cancelled:true}};
        const data=command==='backup.export'?service.exportData():{app:'WinOptimizer Aion',version:app.getVersion(),created:new Date().toISOString(),health:service.latestHealth,diagnostics:service.diagnostics.report,activity:service.state};
        await fsp.writeFile(result.filePath,JSON.stringify(data,null,2),'utf8');return {ok:true,data:{saved:true}};
      }
      if(command==='backup.import'){
        const result=await dialog.showOpenDialog(window,{properties:['openFile'],filters:[{name:'JSON',extensions:['json']}]});if(result.canceled)return {ok:true,data:{cancelled:true}};
        const stat=await fsp.stat(result.filePaths[0]);if(stat.size>5*1024*1024)throw Error('BACKUP_INVALID');
        return {ok:true,data:service.importData(JSON.parse(await fsp.readFile(result.filePaths[0],'utf8')))};
      }
      if(command==='updates.check'){if(service.busy||updating)throw Error('OPERATION_BUSY');updating=true;try{return {ok:true,data:await updater.check(service.settings.data.channel)};}finally{updating=false;}}
      if(command==='updates.install'){
        if(service.busy||updating)throw Error('OPERATION_BUSY');if(process.platform!=='win32')throw Error('WINDOWS_ONLY');if(payload.confirm!==true)throw Error('CONFIRM_REQUIRED');updating=true;
        try{const file=await updater.download();service.settings.save(service.settings.data);service.save();
          // Detached installer waits for the application to close. The validated bytes are never handed to a shell.
          const child=spawn(file,['/S','--updated','--force-run'],{detached:true,stdio:'ignore',windowsHide:true});await new Promise((resolve,reject)=>{child.once('spawn',resolve);child.once('error',reject);});child.unref();updating=false;setTimeout(()=>app.quit(),500);return {ok:true,data:{installing:true}};
        }catch(e){updating=false;throw e;}
      }
      return {ok:true,data:await service.handle(command,payload)};
    }catch(e){const error=/^[A-Z][A-Z0-9_]+$/.test(e.message)?e.message:'OPERATION_FAILED';return {ok:false,error};}
  });
  window.on('close',e=>{if(service.busy||updating){e.preventDefault();dialog.showMessageBox(window,{type:'info',message:language()?'Please wait for the current operation to finish.':'Lütfen devam eden işlemin bitmesini bekleyin.',buttons:[language()?'OK':'Tamam']});}});
  await window.loadFile(path.join(__dirname,'../dist/index.html'));
});
app.on('window-all-closed',()=>app.quit());
}
