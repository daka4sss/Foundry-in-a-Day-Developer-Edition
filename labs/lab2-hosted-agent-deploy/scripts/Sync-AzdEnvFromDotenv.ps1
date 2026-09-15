# Sync values from .env into the current azd environment.
# Usage:
#   .\scripts\Sync-AzdEnvFromDotenv.ps1
# Optional:
#   .\scripts\Sync-AzdEnvFromDotenv.ps1 -EnvFile .\.env

[CmdletBinding()]
param(
    [string]$EnvFile = (Join-Path (Split-Path -Parent $PSScriptRoot) ".env")
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $EnvFile)) {
    Write-Error ".env が見つかりません: $EnvFile`n.env.example をコピーして値を編集してください。"
    exit 1
}

if (-not (Get-Command azd -ErrorAction SilentlyContinue)) {
    Write-Error "azd コマンドが見つかりません。Azure Developer CLI をインストールしてください。"
    exit 1
}

Write-Host "Reading $EnvFile ..."
$count = 0
Get-Content -LiteralPath $EnvFile | ForEach-Object {
    $line = $_.Trim()
    if (-not $line -or $line.StartsWith("#")) { return }

    $idx = $line.IndexOf("=")
    if ($idx -lt 1) { return }

    $key = $line.Substring(0, $idx).Trim()
    $val = $line.Substring($idx + 1).Trim()

    # 前後の引用符を除去
    # Remove surrounding quotation marks
    if (($val.StartsWith('"') -and $val.EndsWith('"')) -or
        ($val.StartsWith("'") -and $val.EndsWith("'"))) {
        $val = $val.Substring(1, $val.Length - 2)
    }

    if (-not $val) {
        Write-Warning "値が空のためスキップ: $key"
        return
    }

    Write-Host "azd env set $key ***" -ForegroundColor Cyan
    & azd env set $key $val
    if ($LASTEXITCODE -ne 0) {
        Write-Error "azd env set に失敗しました: $key"
        exit 1
    }
    $count++
}

Write-Host "`nDone. $count 個の環境変数を azd 環境に登録しました。" -ForegroundColor Green
