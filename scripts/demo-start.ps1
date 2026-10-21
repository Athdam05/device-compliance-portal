# Starts everything the live demo needs (safe to run repeatedly - it only starts what is not already up)
# and prints a status table at the end.
#   powershell -ExecutionPolicy Bypass -File scripts\demo-start.ps1
$ErrorActionPreference = 'Continue'
$tools   = Join-Path $env:USERPROFILE 'tools'
$project = Split-Path -Parent $PSScriptRoot

function Test-Port($port) { [bool](Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue) }
function Get-Code($url)   { try { (Invoke-WebRequest $url -UseBasicParsing -TimeoutSec 5).StatusCode } catch { if ($_.Exception.Response) { [int]$_.Exception.Response.StatusCode } else { 0 } } }
function Wait-Until([scriptblock]$cond, [int]$seconds, [string]$what) {
    $end = (Get-Date).AddSeconds($seconds)
    while ((Get-Date) -lt $end) { if (& $cond) { return $true }; Start-Sleep 3 }
    Write-Host "  ! timed out waiting for $what" -ForegroundColor Yellow; return $false
}

# ---- 1. Docker Desktop -------------------------------------------------------------------------------
docker info *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Starting Docker Desktop (takes 1-2 minutes)..."
    Start-Process 'C:\Program Files\Docker\Docker\Docker Desktop.exe'
    Wait-Until { docker info *> $null; $LASTEXITCODE -eq 0 } 240 'Docker engine' | Out-Null
}

# ---- 2. containers: registry, Docker app, Ansible node ---------------------------------------------------
foreach ($c in 'registry', 'dcmp-app', 'dcmp-node') {
    $state = docker inspect -f '{{.State.Running}}' $c 2>$null
    if ($state -eq 'false') { Write-Host "Starting container $c ..."; docker start $c | Out-Null }
    elseif (-not $state)    { Write-Host "Container $c does not exist." -ForegroundColor Yellow
                              if ($c -eq 'dcmp-node') { Write-Host "  create it with:  bash ansible/run.sh up   then   bash ansible/run.sh play" } }
}

# ---- 3. Jenkins (JDK 21, port 9090) -------------------------------------------------------------------
if (-not (Test-Port 9090)) {
    Write-Host "Starting Jenkins ..."
    $env:JENKINS_HOME = Join-Path $tools 'jenkins_home'
    $java = (Get-ChildItem (Join-Path $tools 'jdk21\*\bin\java.exe') | Select-Object -First 1).FullName
    Start-Process -FilePath $java -ArgumentList '-jar', (Join-Path $tools 'jenkins\jenkins.war'), '--httpPort=9090' `
        -RedirectStandardOutput (Join-Path $tools 'jenkins.log') -RedirectStandardError (Join-Path $tools 'jenkins.err') -WindowStyle Hidden
}

# ---- 4. Tomcat (port 8081) -------------------------------------------------------------------------------
if (-not (Test-Port 8081)) {
    Write-Host "Starting Tomcat ..."
    $env:CATALINA_HOME = Join-Path $tools 'apache-tomcat-9.0.98'
    Start-Process -FilePath (Join-Path $env:CATALINA_HOME 'bin\catalina.bat') -ArgumentList 'run' -WorkingDirectory $env:CATALINA_HOME `
        -RedirectStandardOutput (Join-Path $tools 'tomcat.out') -RedirectStandardError (Join-Path $tools 'tomcat.err') -WindowStyle Hidden
}

# ---- 5. wait for health --------------------------------------------------------------------------------------
$checks = @(
    @{ Name = 'Jenkins (CI/CD)';          Url = 'http://localhost:9090/login';                    Open = 'http://localhost:9090' ; Want = 200 },
    @{ Name = 'App on Tomcat';            Url = 'http://localhost:8081/dcmp/actuator/health';     Open = 'http://localhost:8081/dcmp/' ; Want = 200 },
    @{ Name = 'App in Docker container';  Url = 'http://localhost:8092/actuator/health';          Open = 'http://localhost:8092/' ; Want = 200 },
    @{ Name = 'App on Ansible node';      Url = 'http://localhost:8093/actuator/health';          Open = 'http://localhost:8093/' ; Want = 200 },
    @{ Name = 'Docker registry';          Url = 'http://localhost:5000/v2/_catalog';              Open = 'http://localhost:5000/v2/_catalog' ; Want = 200 }
)
Write-Host "`nWaiting for services to answer ..."
foreach ($c in $checks) { Wait-Until { (Get-Code $c.Url) -eq $c.Want } 240 $c.Name | Out-Null }

Write-Host "`n================  DEMO STATUS  ================"
$allOk = $true
foreach ($c in $checks) {
    $ok = (Get-Code $c.Url) -eq $c.Want
    if (-not $ok) { $allOk = $false }
    Write-Host ("{0,-26} {1,-6} {2}" -f $c.Name, $(if ($ok) { 'OK' } else { 'DOWN' }), $c.Open) -ForegroundColor $(if ($ok) { 'Green' } else { 'Red' })
}

# ---- 6. files the Ansible demo needs -------------------------------------------------------------------------
$art = Join-Path $project 'ansible\artifacts'
New-Item -ItemType Directory -Force $art | Out-Null
foreach ($v in '1.0.6', '1.0.7') {
    if (-not (Test-Path (Join-Path $art "app-$v.war"))) { Write-Host "Missing ansible\artifacts\app-$v.war (needed for the Ansible demo)" -ForegroundColor Yellow; $allOk = $false }
}
$bad = Join-Path $art 'app-1.0.8.war'
if (-not (Test-Path $bad)) { Set-Content -Path $bad -Value 'this is not a valid WAR - simulates a corrupted/bad release artefact' -NoNewline; Write-Host "Created the deliberately broken release artefact app-1.0.8.war" }

if ($allOk) { Write-Host "`nAll set. Open Jenkins and sign in BEFORE the demo starts." -ForegroundColor Green }
else        { Write-Host "`nSomething is not ready - see the lines above." -ForegroundColor Yellow }
