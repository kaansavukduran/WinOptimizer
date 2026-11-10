const test=require('node:test');const assert=require('node:assert/strict');const path=require('node:path');const crypto=require('node:crypto');
const {distribution}=require('../desktop/distribution.cjs');const {validateManifest}=require('../desktop/updater.cjs');
test('portable data follows the original executable folder and does not override installed or development data',()=>{
 const folder=path.resolve('portable-fixture'),local=path.resolve('installed-fixture');
 assert.deepEqual(distribution(true,{PORTABLE_EXECUTABLE_DIR:folder},local),{portable:true,data:path.join(folder,'Data')});
 for(const [packaged,env] of [[false,{PORTABLE_EXECUTABLE_DIR:folder}],[true,{}],[true,{PORTABLE_EXECUTABLE_DIR:'relative'}]])assert.deepEqual(distribution(packaged,env,local),{portable:false,data:path.join(local,'WinOptimizer Aion')});
});
test('signed portable metadata is bound to the exact release, filename, size and hash',()=>{
 const {privateKey,publicKey}=crypto.generateKeyPairSync('ed25519');const base='https://github.com/kaansavukduran/WinOptimizer/releases/download/v5.3.1/';const m={schema:1,version:'5.3.1',platform:'win32',arch:'x64',sha256:'a'.repeat(64),bytes:100,url:base+'WinOptimizer-Aion-5.3.1-Windows-x64-Setup.exe',portable:{bytes:120,sha256:'b'.repeat(64),url:base+'WinOptimizer-Aion-5.3.1-Windows-x64-Portable.exe'}};
 const check=value=>{const bytes=Buffer.from(JSON.stringify(value));return validateManifest(bytes,crypto.sign(null,bytes,privateKey).toString('base64'),publicKey,'5.3.0','stable','x64');};assert.equal(check(m).portable.bytes,120);
 for(const portable of [{...m.portable,url:'https://example.org/Portable.exe'},{...m.portable,url:m.url},{...m.portable,bytes:-1},{...m.portable,sha256:'invalid'}])assert.throws(()=>check({...m,portable}),/UPDATE_MANIFEST_INVALID/);
});
