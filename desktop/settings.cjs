const fs = require('node:fs');
const path = require('node:path');
const DEFAULTS = Object.freeze({schema:1,operationDetails:true,followPointer:true,petting:true,mascotSize:100,language:'tr',theme:'dark',scale:100,textSize:100,font:'system',lineHeight:1.5,letterSpacing:0,accent:'#b82e69',density:'comfortable',motion:true,sound:false,gamification:true,companion:true,channel:'beta'});
function normalize(input={}, locale='tr') {
  const out={...DEFAULTS,language:locale.toLowerCase().startsWith('en')?'en':'tr'};
  for (const [k,values] of Object.entries({language:['tr','en'],theme:['light','dark','system','contrast'],font:['system','readable','dyslexic'],density:['comfortable','compact'],channel:['stable','beta']})) if(values.includes(input[k])) out[k]=input[k];
  for(const [k,min,max,step] of [['mascotSize',75,150,5],['scale',80,200,5],['textSize',80,160,5],['lineHeight',1.2,2,0.1],['letterSpacing',0,3,0.1]]) if(Number.isFinite(input[k]) && input[k]>=min && input[k]<=max) out[k]=Math.round(input[k]/step)*step;
  for(const k of ['operationDetails','motion','sound','gamification','companion','followPointer','petting']) if(typeof input[k]==='boolean') out[k]=input[k];
  if(/^#[0-9a-f]{6}$/i.test(input.accent))out.accent=input.accent;
  return out;
}
function atomicWrite(file,value){fs.mkdirSync(path.dirname(file),{recursive:true});const temp=file+'.tmp';fs.writeFileSync(temp,JSON.stringify(value,null,2),{mode:0o600});fs.renameSync(temp,file);}
class Settings {
  constructor(dir,locale){this.file=path.join(dir,'settings.json');this.locale=locale;this.warning=null;this.data=this.read();}
  read(){try{return normalize(JSON.parse(fs.readFileSync(this.file,'utf8')),this.locale);}catch(e){if(e.code!=='ENOENT')this.warning='SETTINGS_RECOVERED';return normalize({},this.locale);}}
  save(input){const next=normalize(input,this.locale);atomicWrite(this.file,next);this.data=next;return next;}
}
module.exports={DEFAULTS,normalize,atomicWrite,Settings};
