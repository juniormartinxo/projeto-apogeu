param(
    [int]$Port = 8501,
    [string]$HostAddress = "127.0.0.1"
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $repoRoot

$python = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python)) {
    throw "Virtualenv not found. Run: python -m venv .venv; .\.venv\Scripts\python.exe -m pip install -r requirements.txt"
}

$tailscale = Get-Command tailscale -ErrorAction SilentlyContinue
if (-not $tailscale) {
    throw "tailscale CLI not found. Install Tailscale and log in before running make share."
}

$streamlitArgs = @(
    "-m", "streamlit", "run", "app.py",
    "--server.address", $HostAddress,
    "--server.port", "$Port",
    "--server.enableCORS", "true",
    "--server.enableXsrfProtection", "true",
    "--browser.gatherUsageStats", "false"
)

$existing = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if ($existing) {
    throw "Port $Port is already in use. Stop that process or pass a free -Port before opening Funnel."
}

Write-Host "Starting Protocolo Apogeu on http://localhost:$Port ..."
Start-Process -FilePath $python -ArgumentList $streamlitArgs -WorkingDirectory $repoRoot -WindowStyle Hidden | Out-Null

$ready = $false
for ($i = 0; $i -lt 30; $i += 1) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$Port" -UseBasicParsing -TimeoutSec 2
        if ($response.StatusCode -eq 200) {
            $ready = $true
            break
        }
    } catch {
        Start-Sleep -Seconds 1
    }
}

if (-not $ready) {
    throw "Streamlit did not respond on http://localhost:$Port."
}

Write-Host "Opening Tailscale Funnel for http://localhost:$Port ..."
tailscale funnel --bg "localhost:$Port"

Write-Host ""
Write-Host "Public URL:"
tailscale funnel status
