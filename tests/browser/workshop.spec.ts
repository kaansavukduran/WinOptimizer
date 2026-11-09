import {test,expect} from '@playwright/test';
async function fixture(page:any){
 await page.addInitScript(()=>{
  const settings={schema:1,language:'tr',theme:'light',scale:100,textSize:100,font:'system',lineHeight:1.5,letterSpacing:0,accent:'#b82e69',density:'comfortable',motion:true,sound:false,gamification:true,companion:true,channel:'stable'};
  let focus:any=null;const calls:any[]=[];(window as any).__calls=calls;
  (window as any).aion={invoke:async(command:string,payload:any)=>{
   calls.push({command,payload});const ok=(data:any)=>({ok:true,data});
   if(command==='bootstrap')return ok({settings,version:'5.2.0',platform:'win32',milestones:[]});
   if(command==='health')return ok({os:'Fixture Windows',build:'fixture',cpu:'Fixture CPU',ramTotal:1000,ramFree:500,boot:'2026-11-09T12:00:00Z',disks:[],physical:[],security:{defender:null,firewall:null,bitlocker:null}});
   if(command==='history')return ok({cleanup:[],events:[],milestones:[]});
   if(command==='operation.status')return ok({phase:'download',bytes:5000,total:10000});
   if(command==='settings.save')return ok(payload);
   if(command==='workshop.library')return ok({packages:[{id:'DriverBackups/fixture',kind:'DriverBackups',at:'2026-11-09T12:00:00Z'}],ignored:[],focus});
   if(command==='package.inspect')return ok({id:'fixture-plan',bytes:10000,candidates:[{id:'wifi.inf',name:'Fixture Wi-Fi',version:'1.0',deviceClass:'Net',eligible:true},{id:'unsigned.inf',name:'Unsigned fixture',eligible:false}]});
   if(command==='package.apply')return ok({success:true,items:[{id:'wifi.inf',success:true,code:0}],changes:[]});
   if(command==='runtime.inventory')return ok({available:true,items:[]});
   if(command==='runtime.prepare')return ok({id:'runtime-plan',bytes:10000,publisher:'Microsoft fixture',sha256:'a'.repeat(64)});
   if(command==='runtime.install')return ok({success:false,code:1,runtime:[]});
   if(command==='focus.inventory')return ok({apps:[],powers:[{id:'balanced',name:'Balanced',active:true}]});
   if(command==='focus.start'){focus={at:'2026-11-09T12:00:00Z'};return ok({success:true,focus});}
   if(command==='focus.stop'){focus=null;return ok({success:false,conflict:true});}
   if(command==='system.open'||command==='external')return ok({opened:true});
   return {ok:false,error:'UNKNOWN_COMMAND'};
  }};
 });
 await page.goto('/');await page.getByRole('button',{name:'Bakım atölyesi',exact:true}).click();await expect(page.getByRole('button',{name:'İncele',exact:true})).toBeVisible();
}
test('driver recovery selects only signed candidates and distinguishes package acceptance from an actual driver change',async({page})=>{
 await fixture(page);await page.getByRole('button',{name:'İncele',exact:true}).click();
 await expect(page.getByRole('checkbox',{name:'Unsigned fixture',exact:true})).toBeDisabled();
 await page.getByRole('checkbox',{name:'Fixture Wi-Fi',exact:true}).check();await page.getByRole('button',{name:'Seçilen sürücü paketlerini uygula (1)',exact:true}).click();
 expect(await page.evaluate(()=>(window as any).__calls.some((c:any)=>c.command==='package.apply'))).toBe(false);
 await page.getByRole('dialog').getByRole('button',{name:'Devam et',exact:true}).click();
 await expect(page.getByText('Windows daha uygun sürücüyü korumuş olabilir. Aygıt sürümünde değişiklik gözlenmedi.',{exact:true})).toBeVisible();
});
test('runtime installation requires explicit license acceptance and failed postchecks never show verified success',async({page})=>{
 await fixture(page);await page.getByRole('button',{name:'Oyun bileşenleri',exact:true}).click();
 await page.getByRole('button',{name:'Microsoft’tan indir ve doğrula',exact:true}).first().click();
 await page.getByRole('button',{name:'Microsoft paketini kur',exact:true}).click();await expect(page.getByRole('dialog').getByRole('button',{name:'Devam et',exact:true})).toBeDisabled();
 await page.getByRole('checkbox',{name:'Microsoft lisans koşullarını kabul ediyorum',exact:true}).check();await page.getByRole('dialog').getByRole('button',{name:'Devam et',exact:true}).click();
 await expect(page.getByText('Kurulum tamamlanamadı veya bileşenin kurulduğu doğrulanamadı.',{exact:true})).toBeVisible();await expect(page.getByText('Bileşenin kurulduğu yeniden kontrol edildi.',{exact:true})).toHaveCount(0);await expect(page.locator('[data-clip="celebrate"]')).toHaveCount(0);
});
test('focus session can end without overwriting a later Windows power-plan choice',async({page})=>{
 await fixture(page);await page.getByRole('button',{name:'Odak ve kurtarma',exact:true}).click();await page.getByRole('button',{name:'Uygulamaları ve güç planlarını göster',exact:true}).click();
 await expect(page.getByText('Kapatma isteği gönderilebilecek kullanıcı penceresi bulunamadı. Yalnızca güç planıyla oturum başlatabilirsin.',{exact:true})).toBeVisible();await page.getByRole('button',{name:'Odak oturumunu başlat',exact:true}).click();await page.getByRole('dialog').getByRole('button',{name:'Devam et',exact:true}).click();await expect(page.getByRole('button',{name:'Önceki güç planına dön',exact:true})).toBeVisible();await page.getByRole('button',{name:'Önceki güç planına dön',exact:true}).click();await page.getByRole('dialog').getByRole('button',{name:'Devam et',exact:true}).click();await expect(page.getByText(/Güç planı Windows’ta değişmiş/)).toBeVisible();
});
test('workshop remains usable in English with 200% scale, 125% text and OpenDyslexic',async({page})=>{
 await fixture(page);await page.getByRole('button',{name:'Ayarlar',exact:true}).click();await page.getByLabel('Dil',{exact:true}).selectOption('en');await page.getByRole('button',{name:'Appearance',exact:true}).click();await page.getByLabel('Theme',{exact:true}).selectOption('contrast');await page.getByRole('button',{name:'200%',exact:true}).click();await page.getByRole('button',{name:'Accessibility',exact:true}).click();await page.getByLabel('Font',{exact:true}).selectOption('dyslexic');await page.getByRole('spinbutton',{name:'Text size only (%)',exact:true}).fill('125');await page.getByRole('spinbutton',{name:'Text size only (%)',exact:true}).press('Enter');await page.setViewportSize({width:540,height:960});await page.getByRole('button',{name:'Care workshop',exact:true}).click();await page.getByRole('button',{name:'Game runtimes',exact:true}).click();await expect(page.getByRole('button',{name:'Download from Microsoft & verify',exact:true}).first()).toBeVisible();expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBe(true);
});
test('Aion success plays once then returns to idle, and offscreen animation pauses',async({page})=>{
 await fixture(page);await page.getByRole('button',{name:'Genel bakış',exact:true}).click();await page.getByRole('button',{name:'Sistemi kontrol et',exact:true}).click();await expect(page.locator('.aion-sprite')).toHaveAttribute('data-clip','celebrate');await expect(page.locator('.aion-sprite')).toHaveAttribute('data-clip','idle',{timeout:2500});await page.getByRole('button',{name:'Bakım atölyesi',exact:true}).click();const sprite=page.locator('.aion-sprite');await expect(sprite).toHaveAttribute('data-animated','true');await page.getByRole('button',{name:'Animasyonu duraklat',exact:true}).click();await expect(sprite).toHaveAttribute('data-animated','false');await page.getByRole('button',{name:'Animasyonu oynat',exact:true}).click();await expect(sprite).toHaveAttribute('data-animated','true');await page.getByRole('heading',{name:'Atlanan güncellemeler',exact:true}).scrollIntoViewIfNeeded();await expect(sprite).toHaveAttribute('data-animated','false');
});
