@echo off
echo Starting Flask Server...
echo.
echo Server will be available at: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.
cd /d %~dp0
python app.py
pause


