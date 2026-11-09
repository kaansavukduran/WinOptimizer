import {test,expect} from '@playwright/test';

test('partial driver installation shows failed items and never celebrates success',async({page})=>{
  // UI-only regression fixture; no device or driver is modified by this test.
  await page.addInitScript(()=>{
    let installed=false;
    const settings={schema:1,language:'tr',theme:'light',scale:100,textSize:100,font:'system',lineHeight:1.5,letterSpacing:0,accent:'#b82e69',density:'comfortable',motion:true,sound:false,gamification:true,companion:true,channel:'stable'};
    const item={id:'00000000-0000-0000-0000-000000000001',name:'Fixture Wi-Fi',bytes:100,manufacturer:'Fixture',model:'Fixture'};
    (window as any).aion={invoke:async(command:string)=>{
      if(command==='bootstrap')return {ok:true,data:{settings,version:'5.0.1',platform:'win32',milestones:[]}};
      if(command==='windows-updates')return {ok:true,data:[item]};
      if(command==='windows-install'){installed=true;return {ok:true,data:{success:false,reboot:false,items:[{...item,success:false,code:4}]}};}
      if(command==='history')return {ok:true,data:{cleanup:[],milestones:[],events:installed?[{id:'fixture-result',type:'windows-install',at:'2026-11-09T12:00:00Z',success:false,items:[{...item,success:false,code:4}]}]:[]}};
      return {ok:false,error:'UNKNOWN_COMMAND'};
    }};
  });
  await page.goto('/');
  await page.getByRole('button',{name:'Sürücü merkezi',exact:true}).click();
  await page.getByRole('button',{name:'Güncellemeleri kontrol et',exact:true}).click();
  await page.getByRole('checkbox').check();
  await page.getByRole('button',{name:/Seçilenleri yükle/}).click();
  await page.getByRole('dialog').getByRole('button',{name:'Devam et',exact:true}).click();
  await expect(page.getByRole('alert')).toContainText('Bazı öğeler tamamlanamadı');
  await page.getByRole('button',{name:'Genel bakış',exact:true}).click();
  await expect(page.locator('.aion-sprite')).toHaveAttribute('data-clip','help');
  await page.getByRole('button',{name:'Geçmiş ve yedekler',exact:true}).click();
  await expect(page.getByText('Fixture Wi-Fi',{exact:true})).toBeVisible();
  await expect(page.getByText('Başarısız (4)',{exact:true})).toBeVisible();
});
