const fs=require('node:fs');const path=require('node:path');const crypto=require('node:crypto');const cp=require('node:child_process');
const repo='kaansavukduran/WinOptimizer';const run=JSON.parse(fs.readFileSync('build-run.json','utf8'));const publicKey=fs.readFileSync('desktop/update-public-key.pem');
const gh=(args)=>cp.execFileSync('gh',args,{encoding:'utf8',stdio:['ignore','pipe','inherit']});
for(const version of ['5.0.0-beta.1','5.0.0']){
  const folder=path.join('release-metadata',version),bytes=fs.readFileSync(path.join(folder,'aion-update.json')),sig=fs.readFileSync(path.join(folder,'aion-update.sig'),'utf8').trim();
  if(!crypto.verify(null,bytes,publicKey,Buffer.from(sig,'base64')))throw Error('Invalid manifest signature');const manifest=JSON.parse(bytes);
  if(manifest.version!==version||manifest.sourceCommit!==run.head_sha||manifest.platform!=='win32'||manifest.arch!=='x64')throw Error('Build/source mismatch');
  const name=`WinOptimizer-Aion-${version}-Windows-x64-Setup.exe`;const installer=path.join('build-packages','release',name),file=fs.readFileSync(installer);
  if(file.length!==manifest.bytes||crypto.createHash('sha256').update(file).digest('hex')!==manifest.sha256||file.toString('ascii',0,2)!=='MZ')throw Error('Installer mismatch');
  const tag='v'+version;let release;try{release=JSON.parse(gh(['api',`repos/${repo}/releases/tags/${tag}`]));}catch{
    gh(['release','create',tag,'--repo',repo,'--target',manifest.sourceCommit,'--draft','--prerelease','--latest=false','--title',`WinOptimizer Aion ${version}`,'--notes-file',path.join(folder,'notes.md')]);
    const releases=JSON.parse(gh(['api',`repos/${repo}/releases?per_page=30`]));release=releases.find(r=>r.tag_name===tag);if(!release)throw Error('Draft not found');
  }
  if(!release.draft&&release.assets.some(a=>a.name===name))throw Error('Already published; do not replace immutable release');
  for(const f of [installer,...['aion-update.json','aion-update.sig','SHA256SUMS.txt'].map(n=>path.join(folder,n))]){
    const existing=release.assets.find(a=>a.name===path.basename(f));if(existing){if(existing.size!==fs.statSync(f).size)throw Error('Existing asset mismatch');continue;}
    gh(['release','upload',tag,f,'--repo',repo]);
  }
  gh(['release','edit',tag,'--repo',repo,'--draft=false','--prerelease','--latest=false']);
  console.log(`Published verified Windows package: ${tag}, ${manifest.bytes} bytes, source ${manifest.sourceCommit}`);
}
