param([switch]$SkipAdminSetup)

$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true

$environmentFile = Join-Path $PSScriptRoot ".env"
if (-not (Test-Path $environmentFile)) {
    Copy-Item (Join-Path $PSScriptRoot ".env.example") $environmentFile
    $secret = [Convert]::ToHexString([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(48))
    Add-Content $environmentFile "AA_SECRET_KEY=$secret"
}

$oidcKey = Join-Path $PSScriptRoot "oidc-private.pem"
if (-not (Test-Path $oidcKey)) {
    $rsa = [System.Security.Cryptography.RSA]::Create(4096)
    try {
        [System.IO.File]::WriteAllText($oidcKey, $rsa.ExportRSAPrivateKeyPem())
    }
    finally {
        $rsa.Dispose()
    }
}

Push-Location $PSScriptRoot
try {
    docker compose build auth
    if ($LASTEXITCODE -ne 0) { throw "Docker build failed" }
    docker compose run --rm auth python manage.py migrate
    if ($LASTEXITCODE -ne 0) { throw "Alliance Auth migrations failed" }
    docker compose up -d auth wiki
    if ($LASTEXITCODE -ne 0) { throw "Development services failed to start" }

    if (-not $SkipAdminSetup) {
        $adminStatus = @(docker compose exec -T auth python manage.py shell --command "from django.contrib.auth import get_user_model; print('AA_SUPERUSER_EXISTS=' + str(int(get_user_model().objects.filter(is_superuser=True).exists())))")
        if ($LASTEXITCODE -ne 0) { throw "Could not check Alliance Auth admin accounts" }
        if ($adminStatus -contains "AA_SUPERUSER_EXISTS=0") {
            Write-Host "Create an Alliance Auth admin account (choose a password at the prompt):"
            docker compose exec auth python manage.py createsuperuser
            if ($LASTEXITCODE -ne 0) { throw "Alliance Auth admin creation failed" }
        }
        elseif ($adminStatus -notcontains "AA_SUPERUSER_EXISTS=1") {
            throw "Could not read Alliance Auth admin account status"
        }
    }
}
finally {
    Pop-Location
}

$siteUrl = (Get-Content $environmentFile | Where-Object { $_ -match '^AA_SITE_URL=' } | Select-Object -First 1) -replace '^AA_SITE_URL=', ''
$wikiUrl = "http://$(([uri]$siteUrl).Host):3000"
Write-Host "Alliance Auth: $siteUrl"
Write-Host "Wiki.js:       $wikiUrl"
if ($SkipAdminSetup) {
    Write-Host "Admin setup skipped. Run: docker compose exec auth python manage.py createsuperuser"
}