@echo off
title He Thong Gym - Cong Huan Luyen Vien PT (Trainer Web)
cd /d "%~dp0"
echo ========================================================
echo  KHOI CHAY: CONG HUAN LUYEN VIEN PT (TRAINER WEB)
echo ========================================================
".venv\Scripts\python.exe" UI\main_pt.py
if errorlevel 1 (
    echo.
    echo Co loi xay ra khi chay chuong trinh.
    pause
)
