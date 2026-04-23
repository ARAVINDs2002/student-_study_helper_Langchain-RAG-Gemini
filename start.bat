@echo off
echo Starting Student AI Assistant...

:: Start the FastAPI backend in a new command prompt window
start cmd /k "cd backend && ..\venv\Scripts\activate && python -m uvicorn main:app --port 8000"

:: Wait a few seconds for the server to spin up
timeout /t 3 /nobreak > nul

:: Open the index.html frontend in the default web browser
start frontend\index.html

echo Application started! You can close this window.
exit
