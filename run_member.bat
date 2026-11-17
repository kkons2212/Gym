@echo off
title He Thong Gym - Cong Hoi Vien (Member Web)
cd /d "%~dp0"
echo ========================================================
echo  KHOI CHAY: CONG HOI VIEN THE THAO (MEMBER WEB)
echo ========================================================
".venv\Scripts\python.exe" UI\main_member.py
if errorlevel 1 (
    echo.
    echo Co loi xay ra khi chay chuong trinh.
    pause
)
