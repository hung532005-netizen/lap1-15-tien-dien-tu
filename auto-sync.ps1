# Script tu dong dong bo ma nguon len GitHub cho Antigravity IDE
# Chu ky kiem tra mac dinh: 15 giay

$ErrorActionPreference = "Continue"

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host " [AUTO-SYNC] Dang chay tien trinh dong bo GitHub..." -ForegroundColor Green
Write-Host " Nhan Ctrl + C de dung tien trinh bat cu luc nao." -ForegroundColor Yellow
Write-Host "=====================================================" -ForegroundColor Cyan

while ($true) {
    # Kiem tra xem co tep tin nao thay doi hoac chua duoc stage khong
    $status = git status --porcelain
    if ($status) {
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Write-Host "[$timestamp] Phat hien thay doi, dang tu dong dong bo len GitHub..." -ForegroundColor Cyan
        
        # Them toan bo cac tep tin moi hoac chinh sua
        git add -A
        
        # Tao commit voi thoi gian hien tai
        git commit -m "auto: cap nhat tu dong vao $timestamp"
        
        # Day commit len nhanh main cua GitHub
        $pushResult = git push origin main 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[$timestamp] Dong bo len GitHub thanh cong!" -ForegroundColor Green
        } else {
            Write-Host "[$timestamp] Day len GitHub that bai (kiem tra mang hoac xung dot):" -ForegroundColor Red
            Write-Host $pushResult -ForegroundColor DarkRed
        }
    }
    
    # Cho 15 giay truoc khi kiem tra lan tiep theo
    Start-Sleep -Seconds 15
}
