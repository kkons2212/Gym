@echo off
rem ==============================================================================
rem GYM MANAGEMENT SYSTEM - ENVIRONMENT AUTO-SETUP SCRIPT
rem Tu dong phat hien Python, tao .venv, copy .env, cai dat requirements.txt
rem va kich hoat MySQL Docker container neu Docker dang chay.
rem ==============================================================================

chcp 65001 >nul
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8

echo.
echo ========================================================
echo [1/5] Kiem tra file cau hinh bien moi truong (.env)...
echo ========================================================
if not exist ".env" (
    if exist ".env.example" (
        echo [INFO] Chua co file .env, dang tu dong tao tu .env.example...
        copy /y ".env.example" ".env" >nul
        echo [OK] Da tao thanh cong file .env.
    ) else (
        echo [CANH BAO] Khong tim thay .env.example de khoi tao .env!
    )
) else (
    echo [OK] File .env da san sang.
)

echo.
echo ========================================================
echo [2/5] Kiem tra trinh thong dich Python 3.10 tren may...
echo ========================================================
set "SYS_PYTHON="

rem Kiem tra lenh python trong PATH
where python >nul 2>&1
if not errorlevel 1 (
    set "SYS_PYTHON=python"
)

rem Kiem tra cac thu muc cai dat mac dinh tren Windows
if "%SYS_PYTHON%"=="" (
    if exist "%LocalAppData%\Programs\Python\Python310\python.exe" (
        set "SYS_PYTHON=%LocalAppData%\Programs\Python\Python310\python.exe"
    ) else if exist "%ProgramFiles%\Python310\python.exe" (
        set "SYS_PYTHON=%ProgramFiles%\Python310\python.exe"
    ) else if exist "C:\Python310\python.exe" (
        set "SYS_PYTHON=C:\Python310\python.exe"
    )
)

if "%SYS_PYTHON%"=="" (
    echo.
    echo ========================================================
    echo [LOI NGHIEP TRONG] Khong tim thay Python tren he thong!
    echo Vui long cai dat Python 3.10 tai: https://www.python.org/downloads/
    echo Luu y: Nho tich chon vao o "Add Python to PATH" khi cai dat.
    echo ========================================================
    echo.
    pause
    exit /b 1
)
echo [OK] Da tim thay Python: %SYS_PYTHON%

echo.
echo ========================================================
echo [3/5] Kiem tra moi truong ao (.venv)...
echo ========================================================
if not exist ".venv\Scripts\python.exe" (
    echo [INFO] Dang khoi tao moi truong ao .venv...
    "%SYS_PYTHON%" -m venv .venv
    if errorlevel 1 (
        echo [LOI] Khong the khoi tao .venv!
        pause
        exit /b 1
    )
    echo [OK] Da khoi tao xong .venv.
) else (
    echo [OK] Moi truong ao .venv da ton tai.
)

echo.
echo ========================================================
echo [4/5] Kiem tra cac goi thu vien trong requirements.txt...
echo ========================================================
set "VENV_PYTHON=.venv\Scripts\python.exe"

rem Kiem tra nhanh import cac thu vien cot loi
"%VENV_PYTHON%" -c "import PyQt6, cv2, qrcode, requests, mysql.connector, dotenv" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Dang cai dat cac thu vien can thiet tu requirements.txt...
    echo [INFO] Qua trinh nay co the mat 1-2 phut tuy toc do mang...
    "%VENV_PYTHON%" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [LOI] Co loi khi cai dat dependencies qua pip!
        pause
        exit /b 1
    )
    echo [OK] Da cai dat xong toan bo thu vien.
) else (
    echo [OK] Tat ca thu vien can thiet da san sang.
)

echo.
echo ========================================================
echo [5/5] Kiem tra MySQL Docker Container...
echo ========================================================
where docker >nul 2>&1
if not errorlevel 1 (
    docker info >nul 2>&1
    if not errorlevel 1 (
        echo [INFO] Docker dang bat. Dang dam bao MySQL container hoat dong...
        docker-compose up -d mysql >nul 2>&1
        echo [OK] MySQL Docker container da duoc kich hoat.
    ) else (
        echo [CHU Y] Docker Desktop chua duoc bat. Ung dung van mo duoc nhung can Docker de co CSDL that.
    )
) else (
    echo [CHU Y] Khong tim thay lenh Docker. Ung dung se khoi chay o che do offline.
)

echo.
echo ========================================================
echo [HOAN TAT] MOI TRUONG DA SAN SANG!
echo ========================================================
echo.
