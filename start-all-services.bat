@echo off
REM ============================================
REM Start All PCO Services
REM ============================================
echo.
echo ========================================
echo   Starting PCO Services
echo ========================================
echo.

REM Check if Ollama is running
echo [1/5] Checking Ollama status...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo   ^> Ollama is not running. Please start Ollama first.
    echo   ^> Run: ollama serve
    pause
    exit /b 1
) else (
    echo   ^> Ollama is running ✓
)

echo.
echo [2/5] Starting PCO API Wrapper...
start "PCO API Wrapper" cmd /k "cd /d %~dp0 && python src/app.py"
timeout /t 3 /nobreak >nul

echo.
echo [3/5] Starting PCO AI Service...
start "PCO AI Service" cmd /k "cd /d %~dp0pco-ai-service && python src/app.py"
timeout /t 3 /nobreak >nul

echo.
echo [4/5] Verifying services...
timeout /t 5 /nobreak >nul

REM Check API Wrapper
curl -s http://localhost:5000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo   ^> PCO API Wrapper: Running on port 5000 ✓
) else (
    echo   ^> PCO API Wrapper: Failed to start ✗
)

REM Check AI Service
curl -s http://localhost:5001/health >nul 2>&1
if %errorlevel% equ 0 (
    echo   ^> PCO AI Service: Running on port 5001 ✓
) else (
    echo   ^> PCO AI Service: Failed to start ✗
)

echo.
echo [5/5] Starting Interactive Chat...
timeout /t 2 /nobreak >nul
start "PCO Interactive Chat" cmd /k "cd /d %~dp0pco-ai-service && python interactive_chat.py"

echo.
echo ========================================
echo   All Services Started!
echo ========================================
echo.
echo Services running in separate windows:
echo   - PCO API Wrapper: http://localhost:5000
echo   - PCO AI Service:  http://localhost:5001
echo   - Interactive Chat: Ready for commands
echo.
echo Close this window to keep services running.
echo To stop services, close their respective windows.
echo.
pause