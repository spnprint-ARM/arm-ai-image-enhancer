param(
    [string]$Python = 'C:\ArmAI\.venv\Scripts\python.exe',
    [string]$Dist = 'D:\ArmAI_Build\release\dist\ArmAIImageEnhancer',
    [string]$BuildRoot = 'D:\ArmAI_Build\release',
    [string]$Output = '',
    [string]$IconPath = "$PSScriptRoot\ARM.ico",
    [string]$LanguageIcon = "$PSScriptRoot\..\assets\lang.png",
    [string]$Version = '',
    [switch]$ReusePayload,
    [string]$ReusePayloadPath = ''
)
$ErrorActionPreference = 'Stop'
$Compiler = 'C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe'
$SetupSource = Join-Path $PSScriptRoot 'Setup.cs'
$VersionFile = Join-Path $PSScriptRoot 'VERSION'
$Manifest = Join-Path $PSScriptRoot 'requireAdministrator.manifest'
$Spec = Join-Path $PSScriptRoot 'ArmAIImageEnhancer.spec'
$PayloadZip = if ($ReusePayload -and $ReusePayloadPath) { [IO.Path]::GetFullPath($ReusePayloadPath) } else { Join-Path $BuildRoot 'payload.zip' }
$Stub = Join-Path $BuildRoot 'SetupStub.exe'
$Uninstaller = Join-Path $BuildRoot 'Uninstall.exe'
if (!(Test-Path $Compiler)) { throw "C# compiler not found: $Compiler" }
if (!(Test-Path $Python)) { throw "Python runtime not found: $Python" }
if (!(Test-Path -LiteralPath $IconPath)) { throw "Setup icon not found: $IconPath" }
if (!(Test-Path -LiteralPath $LanguageIcon)) { throw "Language icon not found: $LanguageIcon" }
if (!$Version) { $Version = (Get-Content -LiteralPath $VersionFile -Raw).Trim() }
if ($Version -notmatch '^\d+\.\d+\.\d+$') { throw "Version must use major.minor.patch format: $Version" }
if (!$Output) { $Output = Join-Path $PSScriptRoot "setup-V.$Version.exe" }
New-Item -ItemType Directory -Force -Path $BuildRoot | Out-Null
$VersionInfo = Join-Path $BuildRoot 'VersionInfo.cs'
Set-Content -LiteralPath $VersionInfo -Encoding ASCII -Value "using System.Reflection;`r`n[assembly: AssemblyVersion(`"$Version.0`")]`r`n[assembly: AssemblyFileVersion(`"$Version.0`")]"
if (!(Test-Path $Dist)) {
    $DistParent = Split-Path -Parent $Dist
    $PyWork = Join-Path $BuildRoot 'pyinstaller_work'
    New-Item -ItemType Directory -Force -Path $DistParent,$PyWork | Out-Null
    & $Python -m PyInstaller --clean --noconfirm --distpath $DistParent --workpath $PyWork $Spec
    if ($LASTEXITCODE -ne 0 -or !(Test-Path $Dist)) { throw 'Application bundle creation failed.' }
}
if ($ReusePayload) {
    if (!(Test-Path -LiteralPath $PayloadZip)) { throw "Reusable payload not found: $PayloadZip" }
} else {
    $Stage = Join-Path $BuildRoot 'stage'
    if (Test-Path $Stage) { Remove-Item -LiteralPath $Stage -Recurse -Force }
    New-Item -ItemType Directory -Force -Path $Stage | Out-Null
    Copy-Item -Path (Join-Path $Dist '*') -Destination $Stage -Recurse -Force
    $ProjectRoot = Split-Path -Parent $PSScriptRoot
    Copy-Item -LiteralPath (Join-Path $ProjectRoot 'licenses') -Destination $Stage -Recurse -Force
    Copy-Item -LiteralPath (Join-Path $ProjectRoot 'THIRD_PARTY_NOTICES.txt') -Destination $Stage -Force
    & $Compiler /nologo /target:winexe /platform:x64 /optimize+ "/win32manifest:$Manifest" "/win32icon:$IconPath" /reference:System.Windows.Forms.dll /reference:System.Drawing.dll /reference:System.IO.Compression.dll /reference:System.IO.Compression.FileSystem.dll "/resource:$LanguageIcon,lang.png" "/out:$Uninstaller" $SetupSource $VersionInfo
    if ($LASTEXITCODE -ne 0) { throw 'Uninstaller compilation failed.' }
    Copy-Item -LiteralPath $Uninstaller -Destination (Join-Path $Stage 'Uninstall.exe') -Force
    if (Test-Path $PayloadZip) { Remove-Item -LiteralPath $PayloadZip -Force }
    & $Python (Join-Path $PSScriptRoot 'make_payload.py') $Stage $PayloadZip
    if ($LASTEXITCODE -ne 0) { throw 'Payload archive creation failed.' }
}
& $Compiler /nologo /target:winexe /platform:x64 /optimize+ "/win32manifest:$Manifest" "/win32icon:$IconPath" /reference:System.Windows.Forms.dll /reference:System.Drawing.dll /reference:System.IO.Compression.dll /reference:System.IO.Compression.FileSystem.dll "/resource:$LanguageIcon,lang.png" "/out:$Stub" $SetupSource $VersionInfo
if ($LASTEXITCODE -ne 0) { throw 'Installer stub compilation failed.' }
$Output = [IO.Path]::GetFullPath($Output)
$OutputParent = Split-Path -Parent $Output
New-Item -ItemType Directory -Force -Path $OutputParent | Out-Null
$PayloadBase = Join-Path $OutputParent (([IO.Path]::GetFileNameWithoutExtension($Output)) + '.dat')
$Building = $Output + '.new'
$Previous = $Output + '.previous'
foreach ($temporary in @($Building, $Previous)) {
    if (Test-Path $temporary) { Remove-Item -LiteralPath $temporary -Force }
}
Copy-Item -LiteralPath $Stub -Destination $Building
$ChunkBytes = [long](1.90 * 1024 * 1024 * 1024)
$PayloadParts = @()
$inputStream = [IO.File]::OpenRead($PayloadZip)
try {
    $index = 1
    while ($inputStream.Position -lt $inputStream.Length) {
        $part = '{0}.{1:D3}' -f $PayloadBase, $index
        $partBuilding = $part + '.new'
        if (Test-Path $partBuilding) { Remove-Item -LiteralPath $partBuilding -Force }
        $outputStream = [IO.File]::Create($partBuilding)
        try {
            $remaining = [Math]::Min($ChunkBytes, $inputStream.Length - $inputStream.Position)
            $buffer = New-Object byte[] (4 * 1024 * 1024)
            while ($remaining -gt 0) {
                $read = $inputStream.Read($buffer, 0, [int][Math]::Min($buffer.Length, $remaining))
                if ($read -le 0) { throw 'Unexpected end of payload while splitting data parts.' }
                $outputStream.Write($buffer, 0, $read)
                $remaining -= $read
            }
        } finally { $outputStream.Dispose() }
        $PayloadParts += [PSCustomObject]@{ Final = $part; Building = $partBuilding; Previous = ($part + '.previous') }
        $index++
    }
} finally { $inputStream.Dispose() }
foreach ($part in $PayloadParts) { if (Test-Path $part.Previous) { Remove-Item -LiteralPath $part.Previous -Force } }
$OldPayloads = @()
for ($index = 1; $index -le 20; $index++) {
    $part = '{0}.{1:D3}' -f $PayloadBase, $index
    if (Test-Path $part) { $OldPayloads += $part }
}
if (Test-Path $PayloadBase) { $OldPayloads += $PayloadBase }
$oldExeMoved = $false
$newExeMoved = $false
$oldPayloadMoved = @()
$newPayloadMoved = @()
try {
    if (Test-Path $Output) { Move-Item -LiteralPath $Output -Destination $Previous; $oldExeMoved = $true }
    foreach ($oldPayload in $OldPayloads) {
        $backup = $oldPayload + '.previous'
        if (Test-Path $backup) { Remove-Item -LiteralPath $backup -Force }
        Move-Item -LiteralPath $oldPayload -Destination $backup
        $oldPayloadMoved += [PSCustomObject]@{ Original = $oldPayload; Backup = $backup }
    }
    Move-Item -LiteralPath $Building -Destination $Output
    $newExeMoved = $true
    foreach ($part in $PayloadParts) {
        Move-Item -LiteralPath $part.Building -Destination $part.Final
        $newPayloadMoved += $part.Final
    }
} catch {
    foreach ($newPayload in $newPayloadMoved) { if (Test-Path $newPayload) { Remove-Item -LiteralPath $newPayload -Force } }
    if ($newExeMoved -and (Test-Path $Output)) { Remove-Item -LiteralPath $Output -Force }
    foreach ($oldPayload in $oldPayloadMoved) { if (Test-Path $oldPayload.Backup) { Move-Item -LiteralPath $oldPayload.Backup -Destination $oldPayload.Original } }
    if ($oldExeMoved -and (Test-Path $Previous)) { Move-Item -LiteralPath $Previous -Destination $Output }
    throw
}
if (Test-Path $Previous) { Remove-Item -LiteralPath $Previous -Force }
foreach ($oldPayload in $oldPayloadMoved) { if (Test-Path $oldPayload.Backup) { Remove-Item -LiteralPath $oldPayload.Backup -Force } }
Get-Item -LiteralPath (@($Output) + @($PayloadParts | ForEach-Object { $_.Final })) | Select-Object FullName,Length,LastWriteTime
