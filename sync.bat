@echo off
:: Tep tin day nhanh toan bo thay doi len GitHub ngay lap tuc
title Quick Git Push
echo Dang them tep tin va day len GitHub...
git add -A
git commit -m "update: cap nhat ma nguon"
git push origin main
echo.
echo Hoan tat dong bo!
timeout /t 3
