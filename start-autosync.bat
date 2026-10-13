@echo off
:: Tep tin khoi chay tien trinh tu dong dong bo GitHub
title GitHub Auto-Sync (Antigravity)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0auto-sync.ps1"
pause
