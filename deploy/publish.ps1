# 构建 + 打包，产物：deploy\card-guide-site.zip（直接拖进 EdgeOne Pages / Cloudflare Pages）
$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

Write-Host '==> 1/3 构建站点 (npm run build)' -ForegroundColor Cyan
npm run build
if ($LASTEXITCODE -ne 0) { throw '构建失败，已中止打包' }

$dist = Join-Path $root 'dist'
if (-not (Test-Path $dist)) { throw "没有找到输出目录：$dist" }

$zip = Join-Path $PSScriptRoot 'card-guide-site.zip'
if (Test-Path $zip) { Remove-Item $zip -Force }

Write-Host '==> 2/3 打包 dist -> card-guide-site.zip' -ForegroundColor Cyan
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

$base = (Resolve-Path $dist).Path.TrimEnd('\')
$zipStream = [System.IO.File]::Open($zip, [System.IO.FileMode]::Create)
$archive = New-Object System.IO.Compression.ZipArchive($zipStream, [System.IO.Compression.ZipArchiveMode]::Create)
try {
    Get-ChildItem $dist -Recurse -File | ForEach-Object {
        # 压缩包内一律用 / 分隔，否则 Linux 端解压会生成 "a\b" 这种错误文件名
        $rel = $_.FullName.Substring($base.Length + 1).Replace('\', '/')
        $entry = $archive.CreateEntry($rel, [System.IO.Compression.CompressionLevel]::Optimal)
        $out = $entry.Open()
        $in = [System.IO.File]::OpenRead($_.FullName)
        try { $in.CopyTo($out) } finally { $in.Dispose(); $out.Dispose() }
    }
} finally {
    $archive.Dispose()
    $zipStream.Dispose()
}

Write-Host '==> 3/3 校验压缩包' -ForegroundColor Cyan
$check = [System.IO.Compression.ZipFile]::OpenRead($zip)
try {
    $bad = @($check.Entries | Where-Object { $_.FullName -like '*\*' })
    $hasIndex = @($check.Entries | Where-Object { $_.FullName -eq 'index.html' }).Count -eq 1
    $count = $check.Entries.Count
} finally {
    $check.Dispose()
}
if ($bad.Count -gt 0) { throw "压缩包内有 $($bad.Count) 个路径使用了反斜杠，会影响部署" }
if (-not $hasIndex) { throw '压缩包根目录缺少 index.html' }

$files = Get-ChildItem $dist -Recurse -File
$mb = [math]::Round((($files | Measure-Object Length -Sum).Sum / 1MB), 2)
Write-Host ''
Write-Host "完成：$count 个文件，共 $mb MB，根目录有 index.html，路径校验通过" -ForegroundColor Green
Write-Host "产物：$zip" -ForegroundColor Green
Write-Host '下一步：控制台 → 创建项目 → 直接上传 → 拖入这个 zip → 加速区域选「全球可用区（不含中国大陆）」'

# npm 会把进度写到 stderr，PowerShell 会记成错误记录，这里显式返回成功
exit 0
