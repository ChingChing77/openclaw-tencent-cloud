# Windows 垃圾清理 Bot
# PowerShell 版本
# 以管理员身份运行效果更好

Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "         🧹 Windows 系统垃圾清理" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""

# 检查管理员权限
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "⚠️ 建议以管理员身份运行此脚本！" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "即将清理以下内容：" -ForegroundColor White
Write-Host "   [1] Windows 临时文件"
Write-Host "   [2] 用户临时文件"
Write-Host "   [3] 浏览器缓存 (Chrome/Edge)"
Write-Host "   [4] Windows 更新缓存"
Write-Host "   [5] 日志文件"
Write-Host ""
Write-Host "==============================================" -ForegroundColor Cyan

$confirm = Read-Host "确认开始清理? (Y/N)"
if ($confirm -ne "Y" -and $confirm -ne "y") {
    Write-Host "已取消清理。" -ForegroundColor Yellow
    exit
}

Write-Host ""
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "         🧹 正在清理..." -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""

# 1. Windows 临时文件
Write-Host "[1/5] 清理 Windows 临时文件..." -ForegroundColor Green
Remove-Item -Path "$env:WINDIR\Temp\*" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$env:LOCALAPPDATA\Temp\*" -Recurse -Force -ErrorAction SilentlyContinue

# 2. 用户缓存
Write-Host "[2/5] 清理用户缓存..." -ForegroundColor Green
Remove-Item -Path "$env:LOCALAPPDATA\Microsoft\Windows\INetCache\*" -Recurse -Force -ErrorAction SilentlyContinue

# 3. 浏览器缓存
Write-Host "[3/5] 清理浏览器缓存..." -ForegroundColor Green
Remove-Item -Path "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Cache\*" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$env:LOCALAPPDATA\Microsoft\Edge\User Data\Default\Cache\*" -Recurse -Force -ErrorAction SilentlyContinue

# 4. Windows 更新缓存
Write-Host "[4/5] 清理更新缓存..." -ForegroundColor Green
try {
    Stop-Service -Name wuauserv -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
    Remove-Item -Path "$env:WINDIR\SoftwareDistribution\Download\*" -Recurse -Force -ErrorAction SilentlyContinue
    Start-Service -Name wuauserv -ErrorAction SilentlyContinue
} catch {
    # 权限不足时跳过
}

# 5. 清理日志
Write-Host "[5/5] 清理日志文件..." -ForegroundColor Green
Get-ChildItem -Path "$env:WINDIR\Logs" -Filter "*.log" -Recurse -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue

# 额外：清理回收站
Write-Host ""
Write-Host "[额外] 清理回收站..." -ForegroundColor Green
Clear-RecycleBin -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "         ✅ 清理完成！" -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "已清理：" -ForegroundColor White
Write-Host "   - 临时文件"
Write-Host "   - 浏览器缓存"
Write-Host "   - 更新缓存"
Write-Host "   - 日志文件"
Write-Host "   - 回收站"
Write-Host ""

# 暂停等待用户查看
Write-Host "按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
