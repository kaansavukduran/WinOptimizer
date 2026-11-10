"""Build Windows-only Python/Qt packages with a bundled headless Node runtime."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
NODE_VERSION = '24.22.1'
NODE_SHA256 = 'd702daa815eabbff763c7d3808e235cf031cf2ca70211b56847bc72f51e240e5'

def main():
    if sys.platform != 'win32':
        raise SystemExit('Windows x64 build required')
    version = json.loads((ROOT / 'package.json').read_text())['version']
    payload = ROOT / 'native-build/payload'
    if payload.exists():
        shutil.rmtree(payload)
    payload.mkdir(parents=True)
    for folder in ['backend', 'public/assets', 'public/fonts']:
        shutil.copytree(ROOT / folder, payload / folder)
    (payload / 'native').mkdir()
    shutil.copy2(ROOT / 'native/locales.json', payload / 'native/locales.json')
    (payload / 'desktop').mkdir()
    for file in (ROOT / 'desktop').iterdir():
        if file.suffix == '.cjs' and file.name not in ['main.cjs', 'preload.cjs', 'distribution.cjs'] or file.name == 'update-public-key.pem':
            shutil.copy2(file, payload / 'desktop' / file.name)
    for name in ['package.json', 'LICENSE', 'THIRD_PARTY_NOTICES.md']:
        shutil.copy2(ROOT / name, payload / name)
    vendor = payload / 'vendor'
    vendor.mkdir()
    node = ROOT / 'vendor/node.exe'
    node.parent.mkdir(exist_ok=True)
    if not node.exists() or hashlib.sha256(node.read_bytes()).hexdigest() != NODE_SHA256:
        urllib.request.urlretrieve(f'https://nodejs.org/dist/v{NODE_VERSION}/win-x64/node.exe', node)
    if hashlib.sha256(node.read_bytes()).hexdigest() != NODE_SHA256:
        raise SystemExit('Bundled Node hash mismatch')
    shutil.copy2(node, vendor / 'node.exe')
    urllib.request.urlretrieve(f'https://raw.githubusercontent.com/nodejs/node/v{NODE_VERSION}/LICENSE', vendor / 'NODE-LICENSE.txt')
    shutil.copytree(ROOT / 'native/licenses', payload / 'native/licenses')
    name = f'WinOptimizer-Aion-{version}-Windows-x64-Portable'
    command = [sys.executable, '-m', 'PyInstaller', '--onefile', '--windowed', '--clean', '--noconfirm', '--name', name,
        '--distpath', str(ROOT / 'release'), '--workpath', str(ROOT / 'native-build/pyinstaller'), '--specpath', str(ROOT / 'native-build'),
        '--icon', str(ROOT / 'public/assets/aion.ico'), '--paths', str(ROOT / 'native'), '--add-data', str(payload) + ';.',
        '--exclude-module', 'PySide6.QtWebEngineCore', '--exclude-module', 'PySide6.QtWebEngineWidgets', '--exclude-module', 'PySide6.QtWebEngineQuick',
        '--exclude-module', 'PySide6.QtQml', '--exclude-module', 'PySide6.QtQuick', '--exclude-module', 'PySide6.QtWebChannel',
        str(ROOT / 'native/app.py')]
    subprocess.run(command, cwd=ROOT, check=True)
    from PyInstaller.archive.readers import CArchiveReader
    entries=list(CArchiveReader(str(ROOT/'release'/f'{name}.exe')).toc)
    forbidden=[entry for entry in entries if any(token in entry.lower() for token in ['qtwebengine','chromium','electron','chrome_100','chrome_200'])]
    if forbidden:raise SystemExit('Unexpected browser engine payload: '+repr(forbidden))
    print('Verified native package: no Electron, Chromium or Qt WebEngine payload')
    nsis = shutil.which('makensis') or str(Path(os.environ.get('ProgramFiles(x86)', r'C:\Program Files (x86)')) / 'NSIS/makensis.exe')
    subprocess.run([nsis, f'/DAPP_VERSION={version}', str(ROOT / 'scripts/native-installer.nsi')], cwd=ROOT, check=True)
    files = list((ROOT / 'release').glob(f'*{version}*exe'))
    print(json.dumps([dict(name=f.name, bytes=f.stat().st_size, sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in files], indent=2))

if __name__ == '__main__':
    main()
