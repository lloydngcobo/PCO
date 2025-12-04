@echo off
REM ============================================
REM Create Desktop Shortcut for PCO Services
REM ============================================

set SCRIPT_DIR=%~dp0
set DESKTOP=%USERPROFILE%\Desktop

echo.
echo Creating desktop shortcut for PCO Services...
echo.

REM Create VBS script to create shortcut
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%DESKTOP%\Start PCO Services.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%SCRIPT_DIR%start-all-services.bat" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%SCRIPT_DIR%" >> CreateShortcut.vbs
echo oLink.Description = "Start PCO API Wrapper and AI Service" >> CreateShortcut.vbs
echo oLink.IconLocation = "C:\Windows\System32\shell32.dll,137" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs

REM Execute VBS script
cscript CreateShortcut.vbs >nul

REM Clean up
del CreateShortcut.vbs

echo ✓ Desktop shortcut created successfully!
echo.
echo You can now start PCO services by double-clicking:
echo   "Start PCO Services" on your desktop
echo.
pause