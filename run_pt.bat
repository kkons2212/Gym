@echo off
chcp 65001 >nul
title He Thong Gym - Cong Huan Luyen Vien PT (Trainer Web)
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PYTHONPATH=%~dp0;%~dp0UI;%PYTHONPATH%

echo ========================================================
echo  KHOI CHAY: CONG HUAN LUYEN VIEN PT (TRAINER WEB)
echo ========================================================

rem 1. Tu dong kiem tra va thiet lap day du moi truong (Python, .venv, .env, pip, Docker)
call setup_env.bat
if errorlevel 1 (
    echo [LOI] Thiet lap moi truong that bai. Khong the khoi chay.
    pause
    exit /b 1
)

rem 2. Khoi chay ung dung giao dien
echo [RUN] Dang khoi chay giao dien...
".venv\Scripts\python.exe" UI\main_pt.py
if errorlevel 1 (
    echo.
    echo ========================================================
    echo [CANH BAO] Chuong trinh da ket thuc voi ma loi.
    echo ========================================================
    pause
)
