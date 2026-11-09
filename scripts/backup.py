"""Tracked-source ZIP and all reachable Git history, without credentials."""
import datetime, hashlib, json, pathlib, re, subprocess, zipfile
root=pathlib.Path(__file__).resolve().parents[1]
def git(*args): return subprocess.check_output(['git',*args],cwd=root)
sha=git('rev-parse','HEAD').decode().strip()
branch=git('branch','--show-current').decode().strip()
out=root/'work'/'backups'/sha[:12];out.mkdir(parents=True,exist_ok=True)
files=git('ls-tree','-r','--name-only','HEAD').decode().splitlines()
for file in files:
    data=git('show',f'HEAD:{file}')
    if re.search(rb'-----BEGIN (?:RSA |EC |OPENSSH |ENCRYPTED )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{30,}|AKIA[0-9A-Z]{16}',data):
        raise SystemExit('Secret-like material detected; stopped in '+file)
source=out/f'WinOptimizer-{sha[:12]}-source.zip'
with zipfile.ZipFile(source,'w',zipfile.ZIP_DEFLATED) as z:
    for file in files:z.writestr('WinOptimizer/'+file,git('show',f'HEAD:{file}'))
with zipfile.ZipFile(source) as z:assert z.testzip() is None
bundle=out/f'WinOptimizer-{sha[:12]}-history.bundle'
subprocess.run(['git','bundle','create',str(bundle),'--all'],cwd=root,check=True)
subprocess.run(['git','bundle','verify',str(bundle)],cwd=root,check=True,stdout=subprocess.DEVNULL)
manifest={'repository':'https://github.com/kaansavukduran/WinOptimizer','branch':branch,'commit':sha,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':[{'name':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [source,bundle]]}
(out/'backup-receipt.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
(out/'repository.txt').write_text(manifest['repository']+'\n',encoding='utf8')
print(json.dumps({'folder':str(out),**manifest},indent=2))
