param([string]$OutputPath)
$ErrorActionPreference = 'Stop'
$metadata = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'GIT-HISTORY-PARTS.json') -Raw | ConvertFrom-Json
if (-not $OutputPath) { $OutputPath = Join-Path $PSScriptRoot $metadata.original_file }
if (Test-Path -LiteralPath $OutputPath) {
    if ((Get-FileHash -LiteralPath $OutputPath -Algorithm SHA256).Hash.ToLowerInvariant() -eq $metadata.sha256) {
        Write-Output "Verified existing Git history bundle: $OutputPath"
        return
    }
    throw "Output already exists with different contents: $OutputPath"
}
foreach ($part in $metadata.parts) {
    $partPath = Join-Path $PSScriptRoot $part.file
    if ((Get-Item -LiteralPath $partPath).Length -ne $part.bytes -or (Get-FileHash -LiteralPath $partPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $part.sha256) { throw "Part verification failed: $($part.file)" }
}
$historyOutput = [System.IO.File]::Open($OutputPath, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write)
try {
    foreach ($part in $metadata.parts) {
        $historyInput = [System.IO.File]::OpenRead((Join-Path $PSScriptRoot $part.file))
        try { $historyInput.CopyTo($historyOutput) } finally { $historyInput.Dispose() }
    }
} finally { $historyOutput.Dispose() }
if ((Get-Item -LiteralPath $OutputPath).Length -ne $metadata.bytes -or (Get-FileHash -LiteralPath $OutputPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $metadata.sha256) { throw 'Reassembled bundle verification failed.' }
Write-Output "Restored and SHA-256 verified Git history bundle: $OutputPath"
