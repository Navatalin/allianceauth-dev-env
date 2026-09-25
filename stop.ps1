$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true

docker compose -f (Join-Path $PSScriptRoot "compose.yml") down
if ($LASTEXITCODE -ne 0) { throw "Docker compose down failed" }