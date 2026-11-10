import {test,expect} from '@playwright/test';

async function fixture(page:any,language:'tr'|'en'){
 // Controlled UI data; the real installed Windows path has separate integration coverage.
 await page.addInitScript(({language}:any)=>{
  const settings={schema:1,language,theme:'dark',scale:100,textSize:100,font:'system',lineHeight:1.5,letterSpacing:0,accent:'#b82e69',density:'comfortable',motion:false,sound:false,gamification:true,companion:true,channel:'stable'};
  const offers=Array.from({length:24},(_,i)=>({id:`offer-${i}`,name:`Fixture driver ${i}`,manufacturer:'Fixture',model:'Fixture',bytes:100}));
  const calls:any[]=[];(window as any).__calls=calls;
  (window as any).aion={invoke:async(command:string,payload:any)=>{
   calls.push({command,payload});const ok=(data:any)=>({ok:true,data});
   if(command==='bootstrap')return ok({settings,version:'5.3.1',platform:'win32',milestones:[]});
   if(command==='settings.save')return ok(payload);if(command==='history')return ok({events:[],cleanup:[],milestones:[]});if(command==='operation.status')return ok(null);
   if(command==='windows-updates')return ok(offers);
   if(command==='diagnostics.scan')return ok({id:'bulk-report',at:'2026-11-10T00:00:00Z',online:payload.online,findings:[...offers.map(o=>({id:`update:${o.id}`,category:'devices',status:'update',reason:'driverUpdate',evidence:{name:o.name},actions:[{id:'update-driver',kind:'update'}]})),{id:'optional',category:'runtimes',status:'optional',reason:'runtimeOptional',evidence:{name:'Optional fixture'},actions:[]}]});
   if(command==='windows-install'||command==='diagnostics.updates')return ok({success:false,items:payload.ids.map((id:string,i:number)=>({id,name:`Fixture driver ${i}`,success:i!==0,code:i===0?4:2})),reboot:true});
   return {ok:false,error:'UNKNOWN_COMMAND'};
  }};
 },{language});await page.goto('/');
}

for(const language of ['tr','en'] as const){
 test(`scan Update all bypasses individual checkboxes and filters, confirms every item, and reports partial failure (${language})`,async({page})=>{
  const tr=language==='tr';await fixture(page,language);
  await page.locator('.nav-item').filter({hasText:tr?'Tara ve Düzelt':'Scan & Fix'}).click();await page.getByRole('button',{name:tr?'Taramayı başlat':'Start scan',exact:true}).click();
  expect(await page.evaluate(()=>(window as any).__calls.find((c:any)=>c.command==='diagnostics.scan').payload)).toEqual({online:true});
  await expect(page.getByRole('heading',{name:tr?'Sıradaki adım':'Next step',exact:true})).toBeVisible();
  await page.getByText(tr?'Sonuçları filtrele':'Filter results',{exact:true}).click();await page.getByRole('combobox',{name:tr?'Sonuç filtresi':'Result filter',exact:true}).selectOption('optional');
  await expect(page.locator('.diagnostic-results').getByRole('checkbox')).toHaveCount(0);
  const all=page.getByRole('button',{name:tr?'Tümünü güncelle (24)':'Update all (24)',exact:true});await all.click();
  const dialog=page.getByRole('dialog');await expect(dialog.getByRole('listitem')).toHaveCount(24);await dialog.getByRole('button',{name:tr?'Vazgeç':'Cancel',exact:true}).click();
  expect(await page.evaluate(()=>(window as any).__calls.some((c:any)=>c.command==='diagnostics.updates'))).toBe(false);
  await all.click();await dialog.getByRole('button',{name:tr?'Uygula ve doğrula':'Apply and verify',exact:true}).click();
  const payload=await page.evaluate(()=>(window as any).__calls.find((c:any)=>c.command==='diagnostics.updates').payload);expect(payload).toEqual({reportId:'bulk-report',ids:Array.from({length:24},(_,i)=>`offer-${i}`),confirm:true});
  await expect(page.getByText(tr?'Yüklenemedi (4)':'Not installed (4)',{exact:true})).toBeVisible();await expect(page.locator('[data-clip="celebrate"]')).toHaveCount(0);
  await page.screenshot({path:`work/screenshots/update-all-${language}.png`,fullPage:true});
 });
 test(`Driver center Update all works without selection and preserves the existing confirmation (${language})`,async({page})=>{
  const tr=language==='tr';await fixture(page,language);await page.getByRole('button',{name:tr?'Sürücü merkezi':'Driver center',exact:true}).click();await page.getByRole('button',{name:tr?'Güncellemeleri kontrol et':'Check for updates',exact:true}).click();
  await expect(page.getByRole('checkbox',{checked:true})).toHaveCount(0);await page.getByRole('button',{name:tr?'Tümünü güncelle (24)':'Update all (24)',exact:true}).click();await expect(page.getByRole('dialog').getByRole('listitem')).toHaveCount(24);
  expect(await page.evaluate(()=>(window as any).__calls.some((c:any)=>c.command==='windows-install'))).toBe(false);
  await page.getByRole('dialog').getByRole('button',{name:tr?'Devam et':'Continue',exact:true}).click();const payload=await page.evaluate(()=>(window as any).__calls.find((c:any)=>c.command==='windows-install').payload);expect(payload.ids).toHaveLength(24);expect(payload.confirm).toBe(true);
  await expect(page.getByRole('alert')).toContainText(tr?'Bazı öğeler tamamlanamadı':'Some items could not finish');
 });
}

test('beginner scan flow retains an explicit offline choice and a one-button path to check drivers',async({page})=>{
 await fixture(page,'tr');await page.locator('.nav-item').filter({hasText:'Tara ve Düzelt'}).click();await page.getByText('Tarama seçenekleri',{exact:true}).click();await page.getByRole('checkbox',{name:'Çevrimiçi kontrolleri de yap',exact:true}).uncheck();await page.getByRole('button',{name:'Taramayı başlat',exact:true}).click();
 expect(await page.evaluate(()=>(window as any).__calls.find((c:any)=>c.command==='diagnostics.scan').payload)).toEqual({online:false});
 await page.getByRole('button',{name:'Sürücü güncellemelerini de tara',exact:true}).click();expect(await page.evaluate(()=>(window as any).__calls.filter((c:any)=>c.command==='diagnostics.scan').at(-1).payload)).toEqual({online:true});
 await page.getByRole('button',{name:'Ayarlar',exact:true}).click();await page.getByRole('button',{name:'Görünüm',exact:true}).click();await page.getByRole('button',{name:'200%',exact:true}).click();await page.setViewportSize({width:540,height:960});await page.locator('.nav-item').filter({hasText:'Tara ve Düzelt'}).click();await page.getByRole('button',{name:'Tümünü güncelle (24)',exact:true}).click();
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBe(true);await page.getByRole('dialog').getByRole('button',{name:'Uygula ve doğrula',exact:true}).scrollIntoViewIfNeeded();await expect(page.getByRole('dialog').getByRole('button',{name:'Uygula ve doğrula',exact:true})).toBeVisible();
});
