$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true

$repositoryRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $repositoryRoot ".venv\Scripts\python.exe"
$authRoot = Join-Path $PSScriptRoot "allianceauth"
$manage = Join-Path $authRoot "manage.py"
$environmentFile = Join-Path $PSScriptRoot ".env"
$env:DJANGO_SETTINGS_MODULE = "local_auth.settings.local"

if (-not (Test-Path $environmentFile)) {
    throw "Missing dev\.env. Run dev\bootstrap.ps1 and add WIKIJS_API_KEY first."
}

Get-Content $environmentFile | ForEach-Object {
    if ($_ -match '^\s*([^#][^=]*)=(.*)$') {
        [Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim(), "Process")
    }
}

if ([string]::IsNullOrWhiteSpace($env:WIKIJS_API_KEY)) {
    throw "WIKIJS_API_KEY is empty in dev\.env"
}
if ([string]::IsNullOrWhiteSpace($env:WIKIJS_OIDC_PROVIDER_KEY)) {
    throw "WIKIJS_OIDC_PROVIDER_KEY is empty in dev\.env. Configure Wiki.js OIDC and sign in first."
}

Push-Location $authRoot
try {
    $validationScript = Join-Path $PSScriptRoot "validate_integration.py"
    & $python $manage shell --command "exec(open(r'$validationScript').read())"
}
finally {
    Pop-Location
}