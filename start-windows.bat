@echo off
REM Start the MyResume backend (FastAPI :8010) and landing page (Next.js :3000).
REM Port 8010 matches landing/.env.local (NEXT_PUBLIC_API_BASE_URL).
REM Note: port 8000 is reserved by a Windows svchost service on this machine,
REM so the API deliberately runs on 8010.
setlocal
set ROOT=%~dp0

echo [1/2] Starting MyResume API on http://localhost:8010 ...
start "myresume-api" cmd /k "cd /d %ROOT%backend && python -m uvicorn main:app --reload --host 127.0.0.1 --port 8010"

echo [2/2] Starting landing page on http://localhost:3000 ...
start "myresume-landing" cmd /k "cd /d %ROOT%landing && npm run dev"

echo.
echo Both servers are starting in separate windows.
echo   API docs : http://localhost:8010/docs
echo   Landing  : http://localhost:3000
echo Close those windows to stop the servers.
endlocal
