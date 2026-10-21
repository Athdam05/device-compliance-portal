# Runs the Selenium suite against the Tomcat deployment through Maven (step 9 demo).
#   powershell -ExecutionPolicy Bypass -File scripts\demo-selenium.ps1            -> headless (fast, no window)
#   powershell -ExecutionPolicy Bypass -File scripts\demo-selenium.ps1 -Visible   -> a real Edge window opens and you can watch the clicks
param([switch]$Visible)
$tools = Join-Path $env:USERPROFILE 'tools'
$env:JAVA_HOME = 'C:\Program Files\Eclipse Adoptium\jdk-11.0.32.101-hotspot'
$mvn = Join-Path $tools 'apache-maven-3.9.9\bin\mvn.cmd'
Set-Location (Split-Path -Parent $PSScriptRoot)
$headless = if ($Visible) { 'false' } else { 'true' }
& $mvn -B test-compile failsafe:integration-test failsafe:verify -Pselenium `
    "-Dbase.url=http://localhost:8081/dcmp" `
    "-Dwebdriver.edge.driver=$tools\edgedriver\msedgedriver.exe" `
    "-Dheadless=$headless"
