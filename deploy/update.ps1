# 改完内容后，一条命令：构建校验 -> 提交 -> 推送 -> GitHub Actions 自动发布
#
# 用法：
#   powershell -ExecutionPolicy Bypass -File deploy\update.ps1
#   powershell -ExecutionPolicy Bypass -File deploy\update.ps1 -Message "补充牌店信息"
#
# Token 从哪来（二选一）：
#   1. 环境变量：$env:GITHUB_TOKEN = 'ghp_xxx'
#   2. 文件：deploy\.token（已在 .gitignore 里，不会传到仓库）

param(
    [string]$Message = ''
)

$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$repo = 'RealwuguQAQ/sve-guide'
$siteUrl = 'https://realwuguqaq.github.io/sve-guide/'
$proxyPort = 17890
$proxyUrl = "http://127.0.0.1:$proxyPort"

# ---------- 1. Token ----------
$token = $env:GITHUB_TOKEN
if (-not $token -and (Test-Path (Join-Path $PSScriptRoot '.token'))) {
    $token = (Get-Content (Join-Path $PSScriptRoot '.token') -Raw).Trim()
}
if (-not $token) {
    Write-Host '缺少 GitHub Token。任选一种：' -ForegroundColor Yellow
    Write-Host '  $env:GITHUB_TOKEN = ''ghp_xxx''' -ForegroundColor Yellow
    Write-Host '  或者把 token 写进 deploy\.token' -ForegroundColor Yellow
    exit 1
}
$remote = "https://x-access-token:$token@github.com/$repo.git"

# ---------- 2. 先本地构建，出错就不推 ----------
Write-Host '==> 1/3 构建校验 (npm run build)' -ForegroundColor Cyan
npm run build
if ($LASTEXITCODE -ne 0) { throw '构建失败，已中止，线上内容保持不变' }

# ---------- 3. 提交 ----------
Write-Host '==> 2/3 提交改动' -ForegroundColor Cyan
git add -A
$changed = git status --porcelain
if (-not $changed) {
    Write-Host '没有需要提交的改动，线上不会变化。' -ForegroundColor Green
    exit 0
}
$changed | ForEach-Object { "    $_" }
if (-not $Message) { $Message = '更新内容 ' + (Get-Date -Format 'yyyy-MM-dd HH:mm') }
git commit -m $Message
if ($LASTEXITCODE -ne 0) { throw '提交失败' }

# ---------- 4. 推送（必要时临时起本地代理，绕开 github.com 的坏 IP）----------
Write-Host '==> 3/3 推送到 GitHub' -ForegroundColor Cyan

$ourProxy = $null
$listening = Test-NetConnection -ComputerName 127.0.0.1 -Port $proxyPort -InformationLevel Quiet -WarningAction SilentlyContinue
if (-not $listening) {
    Write-Host '    启动本地代理（本机把 github.com 解析到了坏 IP，直连推不上去）...' -ForegroundColor DarkGray
    $ourProxy = Start-Process -FilePath 'node' -ArgumentList (Join-Path $PSScriptRoot 'github-proxy.mjs') -WindowStyle Hidden -PassThru
    Start-Sleep -Seconds 2
}

try {
    & git -c "http.proxy=$proxyUrl" -c http.lowSpeedLimit=1000 -c http.lowSpeedTime=60 push $remote main
    if ($LASTEXITCODE -ne 0) { throw '推送失败' }
} finally {
    if ($ourProxy -and -not $ourProxy.HasExited) { $ourProxy.Kill() }
}

Write-Host ''
Write-Host '推送完成。GitHub Actions 正在构建，约 1 分钟后生效：' -ForegroundColor Green
Write-Host "    $siteUrl" -ForegroundColor Green
Write-Host '查看构建进度：https://github.com/RealwuguQAQ/sve-guide/actions' -ForegroundColor DarkGray
