$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true

$environmentFile = Join-Path $PSScriptRoot ".env"
if (-not (Test-Path $environmentFile)) {
    throw "Missing .env. Run .\bootstrap.ps1 first."
}

Push-Location $PSScriptRoot
try {
    docker compose up -d auth wiki
    if ($LASTEXITCODE -ne 0) { throw "Development services failed to start" }
}
finally {
    Pop-Location
}

$siteUrl = (Get-Content $environmentFile | Where-Object { $_ -match '^AA_SITE_URL=' } | Select-Object -First 1) -replace '^AA_SITE_URL=', ''
Write-Host "Alliance Auth: $siteUrl"
Write-Host "Wiki.js:       http://$(([uri]$siteUrl).Host):3000"