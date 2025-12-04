@echo off
REM Simple chat script for Windows
REM Usage: chat.bat "Your message here" [session_id]

setlocal enabledelayedexpansion

set MESSAGE=%~1
set SESSION_ID=%~2

if "%MESSAGE%"=="" (
    echo Usage: chat.bat "Your message here" [session_id]
    echo Example: chat.bat "Hello!" user123
    exit /b 1
)

if "%SESSION_ID%"=="" (
    set SESSION_ID=default
)

echo Sending message to AI...
echo.

curl -X POST http://localhost:5001/api/ai/chat -H "Content-Type: application/json" -d "{\"message\": \"%MESSAGE%\", \"session_id\": \"%SESSION_ID%\"}"

echo.
echo.