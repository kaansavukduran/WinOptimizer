const crypto=require('node:crypto');const fs=require('node:fs/promises');const path=require('node:path');
const REPO='kaansavukduran/WinOptimizer';
function compare(a,b){const pa=a.replace(/^v/,'').split('-'),pb=b.replace(/^v/,'').split('-');const na=pa[0].split('.').map(Number),nb=pb[0].split('.').map(Number);for(let i=0;i<3;i++)if(na[i]!==nb[i])return na[i]>nb[i]?1:-1;if(!pa[1]&&pb[1])return 1;if(pa[1]&&!pb[1])return -1;return (pa[1]||'').localeCompare(pb[1]||'',undefined,{numeric:true});}
function validateManifest(bytes,signature,key,version,channel,arch=process.arch){
  if(!crypto.verify(null,bytes,key,Buffer.from(signature.trim(),'base64')))throw Error('UPDATE_SIGNATURE_INVALID');
  const m=JSON.parse(bytes.toString('utf8'));
  if(m.schema!==1||m.platform!=='win32'||m.arch!==arch||!/^\d+\.\d+\.\d+(?:-beta\.\d+)?$/.test(m.version)||!/^([a-f0-9]{64})$/.test(m.sha256)||!Number.isSafeInteger(m.bytes)||m.bytes<=0||m.bytes>500*1024*1024)throw Error('UPDATE_MANIFEST_INVALID');
  if(channel==='stable'&&m.version.includes('-'))throw Error('UPDATE_CHANNEL_MISMATCH');
  const base=`https://github.com/${REPO}/releases/download/v${m.version}/`;
  if(!m.url.startsWith(base)||!/^WinOptimizer-Aion-[a-zA-Z0-9.-]+-Windows-x64-Setup\.exe$/.test(m.url.slice(base.length)))throw Error('UPDATE_URL_INVALID');
  if(compare(m.version,version)<=0)throw Error('UPDATE_NOT_NEWER');
  return m;
}
async function limitedFetch(url,max,request=fetch){const r=await request(url,{signal:AbortSignal.timeout(30000),headers:{'User-Agent':'WinOptimizer-Aion'}});if(!r.ok)throw Error('UPDATE_NETWORK');if(new URL(r.url||url).protocol!=='https:')throw Error('UPDATE_URL_INVALID');let total=0;const chunks=[];for await(const chunk of r.body){total+=chunk.length;if(total>max)throw Error('UPDATE_TOO_LARGE');chunks.push(chunk);}return Buffer.concat(chunks);}
class Updater {
  constructor(dir,key,version,arch=process.arch){this.dir=dir;this.key=key;this.version=version;this.arch=arch;this.pending=null;}
  async check(channel){this.pending=null;const releases=JSON.parse(await limitedFetch(`https://api.github.com/repos/${REPO}/releases?per_page=30`,2*1024*1024));
    const list=releases.filter(r=>!r.draft&&(channel==='beta'||!r.prerelease)&&/^v\d+\.\d+\.\d+(?:-beta\.\d+)?$/.test(r.tag_name)&&compare(r.tag_name,this.version)>0).sort((a,b)=>compare(b.tag_name,a.tag_name));
    if(!list.length)return {available:false};const release=list[0];const manifest=release.assets.find(a=>a.name==='aion-update.json'),signature=release.assets.find(a=>a.name==='aion-update.sig');if(!manifest||!signature)throw Error('UPDATE_UNSIGNED');
    const bytes=await limitedFetch(manifest.browser_download_url,100000);const sig=await limitedFetch(signature.browser_download_url,1000);
    const m=validateManifest(bytes,sig.toString(),this.key,this.version,channel,this.arch);this.pending=m;return {available:true,...m};}
  async download(){if(!this.pending)throw Error('UPDATE_CHECK_FIRST');const m=this.pending;await fs.mkdir(this.dir,{recursive:true});const file=path.join(this.dir,`WinOptimizer-Aion-${m.version}-Windows-${m.arch}-Setup.exe`),tmp=file+'.partial';
    try{const response=await fetch(m.url,{signal:AbortSignal.timeout(600000)});if(!response.ok||new URL(response.url).protocol!=='https:')throw Error('UPDATE_NETWORK');const handle=await fs.open(tmp,'w',0o600);let size=0;const hash=crypto.createHash('sha256');try{for await(const chunk of response.body){size+=chunk.length;if(size>m.bytes)throw Error('UPDATE_HASH_INVALID');hash.update(chunk);await handle.write(chunk);}}finally{await handle.close();}
      if(size!==m.bytes||hash.digest('hex')!==m.sha256)throw Error('UPDATE_HASH_INVALID');await fs.rename(tmp,file);return file;
    }catch(e){await fs.rm(tmp,{force:true});throw e;}}
}
module.exports={Updater,compare,validateManifest,limitedFetch,REPO};
