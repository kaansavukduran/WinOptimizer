const fs=require('node:fs');const path=require('node:path');const crypto=require('node:crypto');const cp=require('node:child_process');
const repo='kaansavukduran/WinOptimizer';const run=JSON.parse(fs.readFileSync('build-run.json','utf8'));const publicKey=fs.readFileSync('desktop/update-public-key.pem');
const gh=(args,input)=>cp.execFileSync('gh',args,{encoding:'utf8',input:input?JSON.stringify(input):undefined,stdio:['pipe','pipe','inherit']});
const releaseIds={'5.0.0-beta.1':439547840,'5.0.0':439549740};
for(const version of ['5.0.0-beta.1','5.0.0']){
  const folder=path.join('release-metadata',version),bytes=fs.readFileSync(path.join(folder,'aion-update.json')),sig=fs.readFileSync(path.join(folder,'aion-update.sig'),'utf8').trim();
  if(!crypto.verify(null,bytes,publicKey,Buffer.from(sig,'base64')))throw Error('Invalid manifest signature');const manifest=JSON.parse(bytes);
  if(manifest.version!==version||manifest.sourceCommit!==run.head_sha||manifest.platform!=='win32'||manifest.arch!=='x64')throw Error('Build/source mismatch');
  const name=`WinOptimizer-Aion-${version}-Windows-x64-Setup.exe`;const installer=path.join('build-packages','release',name),file=fs.readFileSync(installer);
  if(file.length!==manifest.bytes||crypto.createHash('sha256').update(file).digest('hex')!==manifest.sha256||file.toString('ascii',0,2)!=='MZ')throw Error('Installer mismatch');
  const tag='v'+version;const release=JSON.parse(gh(['api',`repos/${repo}/releases/${releaseIds[version]}`]));if(release.tag_name!==tag)throw Error('Release identity mismatch');
  for(const f of [installer,...['aion-update.json','aion-update.sig','SHA256SUMS.txt'].map(n=>path.join(folder,n))]){
    const existing=release.assets.find(a=>a.name===path.basename(f));if(existing){const data=fs.readFileSync(f);if(existing.size!==data.length||existing.digest!=='sha256:'+crypto.createHash('sha256').update(data).digest('hex'))throw Error('Existing asset mismatch');continue;}
    if(!release.draft)throw Error('Published release missing an asset; refusing mutation');
    gh(['api','--method','POST',`https://uploads.github.com/repos/${repo}/releases/${release.id}/assets?name=${encodeURIComponent(path.basename(f))}`,'-H','Content-Type: application/octet-stream','--input',f]);
  }
  if(release.draft)gh(['api','--method','PATCH',`repos/${repo}/releases/${release.id}`,'--input','-'],{draft:false,prerelease:true,make_latest:'false'});
  console.log(`Published verified Windows package: ${tag}, ${manifest.bytes} bytes, source ${manifest.sourceCommit}`);
}
