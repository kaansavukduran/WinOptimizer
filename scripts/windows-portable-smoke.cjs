const {chromium,expect}=require('@playwright/test');const fs=require('node:fs/promises');const path=require('node:path');const {spawn}=require('node:child_process');const assert=require('node:assert/strict');const net=require('node:net');
const source=process.argv[2];if(!source)throw Error('Pass Portable.exe');
const delay=ms=>new Promise(r=>setTimeout(r,ms));
async function snapshot(file){try{return await fs.readFile(file);}catch(e){if(e.code==='ENOENT')return null;throw e;}}
async function launch(exe){
 const server=net.createServer();await new Promise(r=>server.listen(0,'127.0.0.1',r));const port=server.address().port;await new Promise(r=>server.close(r));
 const child=spawn(exe,[`--remote-debugging-port=${port}`],{stdio:'ignore'});let error;const ended=new Promise(resolve=>{child.once('error',e=>{error=e;resolve();});child.once('exit',resolve);});let browser;
 for(let attempt=0;attempt<120&&!browser;attempt++){if(error)throw error;try{browser=await chromium.connectOverCDP(`http://127.0.0.1:${port}`,{timeout:1500});}catch{await delay(500);}}
 if(!browser)throw Error('PORTABLE_DID_NOT_OPEN');const context=browser.contexts()[0];const page=context.pages()[0]||await context.waitForEvent('page');await page.locator('.app-shell').waitFor();page.setDefaultTimeout(45000);
 return {page,close:async()=>{await page.evaluate(()=>window.close());let timer;try{await Promise.race([ended,new Promise((_,reject)=>{timer=setTimeout(()=>reject(Error('PORTABLE_DID_NOT_CLOSE')),60000);})]);}finally{clearTimeout(timer);}await browser.close();}};
}
(async()=>{
 const folder=path.resolve('work/portable-real');await fs.mkdir(folder,{recursive:true});const exe=path.join(folder,path.basename(source));await fs.copyFile(source,exe);
 const installed=path.join(process.env.LOCALAPPDATA,'WinOptimizer Aion','settings.json'),before=await snapshot(installed);
 let app=await launch(exe),page=app.page;const boot=await page.evaluate(()=>window.aion.invoke('bootstrap'));assert.equal(boot.ok,true);assert.equal(boot.data.portable,true);
 await page.locator('.nav-item').last().click();await page.locator('#language').selectOption('tr');await page.getByRole('button',{name:'Görünüm',exact:true}).click();await page.getByLabel('Tema',{exact:true}).selectOption('dark');const scale=page.getByRole('spinbutton',{name:'Arayüz ölçeği (%)',exact:true});await scale.fill('125');await scale.press('Enter');await expect(page.getByRole('status').filter({hasText:'Kaydedildi'})).toBeVisible();
 await page.getByRole('button',{name:'Güncellemeler',exact:true}).click();await expect(page.getByText(/Portable sürüm: ayarlar/)).toBeVisible();
 await page.getByRole('button',{name:'Genel bakış',exact:true}).click();await page.getByRole('button',{name:'Sistemi kontrol et',exact:true}).click();await expect(page.locator('.busy-banner')).toHaveCount(0,{timeout:180000});await expect(page.locator('.facts')).toContainText('Windows');
 await page.locator('.nav-item').filter({hasText:'Tara ve Düzelt'}).click();await page.getByText('Tarama seçenekleri',{exact:true}).click();await page.getByRole('checkbox',{name:'Çevrimiçi kontrolleri de yap',exact:true}).uncheck();await page.getByRole('button',{name:'Taramayı başlat',exact:true}).click();await expect(page.getByRole('heading',{name:'Sıradaki adım',exact:true})).toBeVisible({timeout:180000});await expect(page.locator('.busy-banner')).toHaveCount(0,{timeout:180000});
 await fs.mkdir('work/screenshots',{recursive:true});await page.screenshot({path:'work/screenshots/windows-portable-scan.png',fullPage:true});await app.close();
 const settings=JSON.parse(await fs.readFile(path.join(folder,'Data','WinOptimizer Aion','settings.json'),'utf8'));assert.equal(settings.theme,'dark');assert.equal(settings.scale,125);assert.equal(settings.language,'tr');assert.deepEqual(await snapshot(installed),before);
 app=await launch(exe);const reopened=await app.page.evaluate(()=>window.aion.invoke('bootstrap'));assert.equal(reopened.data.portable,true);assert.equal(reopened.data.settings.scale,125);assert.equal(reopened.data.settings.theme,'dark');await app.close();
 await fs.writeFile('work/native-portable-verified.json',JSON.stringify({version:boot.data.version,portable:true,reopened:true,installedDataPreserved:true,relativeData:'Data',settings:{theme:settings.theme,scale:settings.scale,language:settings.language}},null,2));console.log('PASS actual Portable.exe launch, native scan, adjacent Data, reopen and installed-data isolation');
})().catch(e=>{console.error(e);process.exit(1);});
