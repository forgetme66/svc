@echo off
echo ===================================
echo System Status Check
echo ===================================
echo.

echo Checking Python installation...
python --version
echo.

echo Checking Node.js installation...
node --version
echo.

echo Checking npm installation...
npm --version
echo.

echo ===================================
echo Checking Port Availability
echo ===================================
echo.

echo Checking if port 5000 (Backend) is available...
netstat -ano | findstr :5000 >nul
if %ERRORLEVEL% EQU 0 (
    echo WARNING: Port 5000 is already in use
) else (
    echo OK: Port 5000 is available
)
echo.

echo Checking if port 5173 (Frontend) is available...
netstat -ano | findstr :5173 >nul
if %ERRORLEVEL% EQU 0 (
    echo WARNING: Port 5173 is already in use
) else (
    echo OK: Port 5173 is available
)
echo.

echo ===================================
echo Checking Backend Dependencies
echo ===================================
cd backend
python -m pip list | findstr Flask > nul
if %ERRORLEVEL% EQU 0 (
    echo OK: Flask is installed
) else (
    echo WARN: Flask not installed, running: pip install -r requirements.txt
    python -m pip install -r requirements.txt
)
cd ..
echo.

echo ===================================
echo Checking Frontend Dependencies
echo ===================================
cd frontend
if exist node_modules (
    echo OK: node_modules exists
) else (
    echo WARN: node_modules not found, running: npm install
    npm install
)
cd ..
echo.

echo ===================================
echo Quick Start Instructions
echo ===================================
echo.
echo Terminal 1 - Start Backend:
echo   cd backend
echo   python app.py
echo.
echo Terminal 2 - Start Frontend:
echo   cd frontend
echo   npm run dev
echo.
echo Then open browser: http://localhost:5173
echo Test API: http://localhost:5000/api/health
echo.
pause
