import {test,expect} from '@playwright/test';

async function fixture(page:any,status:'fixed'|'still-present'|'unverified'='still-present'){
  // Deterministic UI-only fixture. The real Windows inventory is tested separately in Windows CI.
  await page.addInitScript(({status}:any)=>{
    const settings={schema:1,language:'tr',theme:'light',scale:100,textSize:100,font:'system',lineHeight:1.5,letterSpacing:0,accent:'#b82e69',density:'comfortable',motion:true,sound:false,gamification:true,companion:true,channel:'stable'};
    const report={id:'fixture-report',at:'2026-11-09T12:00:00Z',online:false,findings:[{id:'device:missing',category:'devices',status:'issue',reason:'missingDriver',evidence:{name:'Fixture aygıt',code:28},actions:[{id:'device-rescan',kind:'repair'},{id:'drivers',kind:'navigate'}]},{id:'runtime:vc-x86',category:'runtimes',status:'optional',reason:'runtimeOptional',evidence:{name:'vc-x86'},actions:[{id:'visual-cpp',kind:'guide'}]},{id:'devices:summary',category:'devices',status:'info',reason:'deviceSummary',evidence:{healthy:14,disconnected:3},actions:[]}]};
    (window as any).__calls=[];
    (window as any).aion={invoke:async(command:string,payload:any)=>{
      (window as any).__calls.push({command,payload});
      if(command==='bootstrap')return {ok:true,data:{settings,version:'5.1.0',platform:'win32',milestones:[]}};
      if(command==='history')return {ok:true,data:{events:[],cleanup:[],milestones:[]}};
      if(command==='settings.save')return {ok:true,data:payload};
      if(command==='diagnostics.scan')return {ok:true,data:report};
      if(command==='diagnostics.repair')return {ok:true,data:{status,success:status==='fixed',report:{...report,id:'fixture-rechecked'}}};
      if(command==='external')return {ok:true,data:true};
      return {ok:false,error:'UNKNOWN_COMMAND'};
    }};
  },{status});
  await page.goto('/');await page.getByRole('navigation',{name:'Ana gezinme'}).getByRole('button',{name:'Tara ve Düzelt'}).click();
  await page.getByRole('button',{name:'Taramayı başlat',exact:true}).click();
}

test('scan separates optional components, asks before repair and shows unresolved outcome without success feedback',async({page})=>{
  await fixture(page);
  await expect(page.getByText('Fixture aygıt',{exact:true}).first()).toBeVisible();
  const mascot=page.getByRole('button',{name:'Aion’u sev',exact:true});await mascot.scrollIntoViewIfNeeded();const box=(await mascot.boundingBox())!;await page.mouse.move(box.x+box.width/2,Math.max(2,box.y-30));await expect(page.locator('.aion-sprite')).toHaveAttribute('data-direction','0');
  await expect(page.getByRole('button',{name:/İsteğe bağlı/})).toBeVisible();
  await page.getByRole('button',{name:'Aygıtları yeniden algıla',exact:true}).click();
  await expect(page.getByRole('dialog')).toBeVisible();
  expect(await page.evaluate(()=>(window as any).__calls.some((c:any)=>c.command==='diagnostics.repair'))).toBe(false);
  await page.getByRole('button',{name:'Uygula ve doğrula'}).click();
  await expect(page.getByText('İşlem çalıştı; sorun devam ediyor',{exact:true})).toBeVisible();
  await expect(page.getByText('Operation complete.',{exact:true})).toHaveCount(0);
  await expect(page.locator('[data-clip="celebrate"]')).toHaveCount(0);
  const calls=await page.evaluate(()=>(window as any).__calls);
  expect(calls.find((c:any)=>c.command==='diagnostics.scan').payload).toEqual({online:false});
  expect(calls.find((c:any)=>c.command==='diagnostics.repair').payload).toEqual({reportId:'fixture-report',findingId:'device:missing',actionId:'device-rescan',confirm:true});
});

test('official source is guidance only and results remain usable at 200% scale in a narrow window',async({page})=>{
  await fixture(page);
  await page.getByRole('button',{name:'Microsoft Visual C++ kaynağını aç'}).click();
  await expect(page.getByText(/Henüz “düzeltildi” olarak işaretlenmez/)).toBeVisible();
  await expect(page.getByText('Düzeltme doğrulandı',{exact:true})).toHaveCount(0);
  await page.getByRole('navigation',{name:'Ana gezinme'}).getByRole('button',{name:'Ayarlar',exact:true}).click();
  await page.getByRole('button',{name:'Görünüm',exact:false}).click();
  await page.getByRole('button',{name:'200%',exact:true}).click();
  await page.setViewportSize({width:540,height:960});
  await page.getByRole('navigation',{name:'Ana gezinme'}).getByRole('button',{name:'Tara ve Düzelt'}).click();
  await page.getByRole('button',{name:'Yeniden tara',exact:true}).click();
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBe(true);
  await expect(page.getByRole('button',{name:'Aygıtları yeniden algıla',exact:true})).toBeVisible();
  await page.screenshot({path:'work/screenshots/scan-fix-200-percent.png',fullPage:true});
});
