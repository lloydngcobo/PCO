@echo off
REM ============================================
REM Stop All PCO Services
REM ============================================
echo.
echo ========================================
echo   Stopping PCO Services
echo ========================================
echo.

echo [1/2] Stopping PCO API Wrapper (port 5000)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
    if !errorlevel! equ 0 (
        echo   ^> Stopped process %%a ✓
    )
)

echo.
echo [2/2] Stopping PCO AI Service (port 5001)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5001 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
    if !errorlevel! equ 0 (
        echo   ^> Stopped process %%a ✓
    )
)

echo.
echo ========================================
echo   All Services Stopped!
echo ========================================
echo.
pause