import {test,expect} from '@playwright/test';
test('scan results install selected offers after confirmation and show each unsuccessful result',async({page})=>{
 // Explicit UI fixture; no real driver is installed or damaged here.
 await page.addInitScript(()=>{
  const settings={schema:1,language:'tr',theme:'light',scale:100,textSize:100,font:'system',lineHeight:1.5,letterSpacing:0,accent:'#b82e69',density:'comfortable',motion:true,sound:false,gamification:true,companion:true,channel:'stable'};
  const calls:any[]=[];(window as any).__calls=calls;
  (window as any).aion={invoke:async(command:string,payload:any)=>{
   calls.push({command,payload});const ok=(data:any)=>({ok:true,data});
   if(command==='bootstrap')return ok({settings,version:'5.2.0',platform:'win32',milestones:[]});if(command==='history')return ok({events:[],cleanup:[],milestones:[]});if(command==='operation.status')return ok(null);
   if(command==='diagnostics.scan')return ok({id:'current-report',at:'2026-11-09T12:00:00Z',online:true,findings:[{id:'update:offer-a',category:'devices',status:'update',reason:'driverUpdate',evidence:{name:'Fixture Game Ready update'},actions:[{id:'update-driver',kind:'update'}]}]});
   if(command==='diagnostics.updates')return ok({success:false,items:[{id:'offer-a',name:'Fixture Game Ready update',success:false,code:4}],reboot:false});return {ok:false,error:'UNKNOWN_COMMAND'};
  }};
 });
 await page.goto('/');await page.locator('.nav-item').filter({hasText:'Tara ve Düzelt'}).click();await page.getByRole('button',{name:'Taramayı başlat',exact:true}).click();await expect(page.getByRole('button',{name:'Seçilen güncellemeleri yükle (0)',exact:true})).toBeDisabled();
 await page.getByRole('checkbox',{name:'Güncellemeyi seç: Fixture Game Ready update',exact:true}).check();await page.getByRole('button',{name:'Seçilen güncellemeleri yükle (1)',exact:true}).click();expect(await page.evaluate(()=>(window as any).__calls.some((c:any)=>c.command==='diagnostics.updates'))).toBe(false);
 await page.getByRole('dialog').getByRole('button',{name:'Uygula ve doğrula',exact:true}).click();await expect(page.getByText('Yüklenemedi (4)',{exact:true})).toBeVisible();await expect(page.locator('[data-clip="celebrate"]')).toHaveCount(0);const call=await page.evaluate(()=>(window as any).__calls.find((c:any)=>c.command==='diagnostics.updates'));expect(call.payload).toEqual({reportId:'current-report',ids:['offer-a'],confirm:true});
});
