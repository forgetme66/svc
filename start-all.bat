@echo off
echo Starting graduation guidance system...
echo.
echo =================================
echo Starting Backend (Python Flask)
echo =================================
start cmd /k "cd /d %cd%\backend && python -m pip install -r requirements.txt > nul 2>&1 && python app.py"
timeout /t 3
echo.
echo Backend should be running at http://localhost:5000
echo Test health check: http://localhost:5000/api/health
echo.
echo =================================
echo Starting Frontend (Vue + Vite)
echo =================================
start cmd /k "cd /d %cd%\frontend && npm install > nul 2>&1 && npm run dev"
timeout /t 3
echo.
echo Frontend should be running at http://localhost:5173
echo.
echo =================================
echo System startup complete!
echo =================================
echo.
echo Open browser and navigate to: http://localhost:5173
pause
