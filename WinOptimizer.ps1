param([string]$Mode='Normal',[int[]]$Tasks,[switch]$NoRestart,[switch]$Help)
# Compatibility launcher; never runs the historical maintenance commands.
$exe=Join-Path $env:LOCALAPPDATA 'Programs\WinOptimizer Aion\WinOptimizer Aion.exe'
if($Help){Write-Host 'WinOptimizer Aion: Setup.exe dosyasini kurun / Install Setup.exe from GitHub Releases.';return}
if(Test-Path -LiteralPath $exe){Start-Process -FilePath $exe}
else{Write-Host 'WinOptimizer Aion henuz kurulu degil / not installed.';Start-Process 'https://github.com/kaansavukduran/WinOptimizer/releases'}
