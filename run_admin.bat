@echo off
title He Thong Gym - Cong Quan Tri Vien & Le Tan (Desktop)
cd /d "%~dp0"
echo ========================================================
echo  KHOI CHAY: CONG QUAN TRI VIEN & LE TAN (DESKTOP)
echo ========================================================
".venv\Scripts\python.exe" UI\main_admin.py
if errorlevel 1 (
    echo.
    echo Co loi xay ra khi chay chuong trinh.
    pause
)
