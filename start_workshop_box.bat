@echo off
echo Starting PersonalParakeet Workshop Box...
echo.

REM Start Python WebSocket bridge in background
echo Starting Python backend...
start "PersonalParakeet Backend" cmd /c ".venv\Scripts\python.exe workshop_websocket_bridge.py"

REM Wait a moment for backend to initialize
timeout /t 2 /nobreak > nul

REM Start Tauri UI
echo Starting Workshop Box UI...
cd workshop-box-ui
start "Workshop Box UI" cmd /c "npm run tauri dev"

echo.
echo Workshop Box is starting up...
echo.
echo To stop, close both command windows.
echo.
pause