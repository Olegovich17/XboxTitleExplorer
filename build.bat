@echo off
chcp 65001 >nul
setlocal
set PYTHONDONTWRITEBYTECODE=1

echo === Xbox Title Explorer - Build Script ===

where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: Python not found in PATH
    exit /b 1
)

echo.
echo [1/4] Creating virtual environment...
python -m venv venv_build
call venv_build\Scripts\activate.bat

echo.
echo [2/4] Installing dependencies...
pip install --no-cache-dir pyinstaller --disable-pip-version-check
pip install --no-cache-dir PyQt6 --disable-pip-version-check

echo.
echo [3/4] Downloading and extracting UPX...
python -c "import urllib.request, zipfile, os; urllib.request.urlretrieve('https://github.com/upx/upx/releases/download/v3.96/upx-3.96-win64.zip', 'upx.zip'); zipfile.ZipFile('upx.zip').extractall('venv_build'); os.remove('upx.zip'); print('UPX extracted')" 2>nul || echo "UPX not available"
set PATH=venv_build\upx-3.96-win64;%PATH%

echo.
echo [3/4] Cleaning previous build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist "XboxTitleExplorer.spec" del "XboxTitleExplorer.spec"

set BUILD_TYPE=--windowed

echo.
echo [4/4] Building exe...
pyinstaller --onefile ^
    %BUILD_TYPE% ^
    --name "XboxTitleExplorer" ^
    --add-data "resources/locales;resources/locales" ^
    --add-data "resources/icon.ico;resources" ^
    --icon "resources/icon.ico" ^
    --hidden-import PyQt6 ^
    --hidden-import PyQt6.QtCore ^
    --hidden-import PyQt6.QtGui ^
    --hidden-import PyQt6.QtWidgets ^
    --hidden-import PyQt6.QtXml ^
    --hidden-import PyQt6.QtPrintSupport ^
    --hidden-import PyQt6.QtSvg ^
    --hidden-import PyQt6.QtSvgWidgets ^
    --exclude-module urllib3 ^
    --exclude-module certifi ^
    --exclude-module charset_normalizer ^
    --exclude-module idna ^
    main.py

echo.
echo Cleaning build artifacts...
if exist build rmdir /s /q build
if exist "XboxTitleExplorer.spec" del "XboxTitleExplorer.spec"

call venv_build\Scripts\deactivate.bat
rmdir /s /q venv_build

echo.
echo === Build complete! ===
if exist dist\XboxTitleExplorer.exe (
    echo File: dist\XboxTitleExplorer.exe
    dir dist\XboxTitleExplorer.exe
) else (
    echo Error: EXE not found
)
pause
