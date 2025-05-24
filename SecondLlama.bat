@echo off
setlocal enabledelayedexpansion

REM Get the directory where the script is located
set "ScriptDirectory=%~dp0"
REM Change the current directory to the script's directory
cd /d "%ScriptDirectory%"

REM Set title for the console window
title SecondLlama Control Panel

REM Set Python to run in unbuffered mode
set PYTHONUNBUFFERED=1

REM Define color variables
set "Color_Green=[92m"
set "Color_Yellow=[93m"
set "Color_Blue=[94m"
set "Color_Red=[91m"
set "Color_Magenta=[95m"
set "Color_Cyan=[96m"
set "Color_White=[97m"
set "Color_Reset=[0m"

REM --- Main Menu Loop ---
:MainMenu
cls
echo %Color_Cyan%================================================================================%Color_Reset%
echo %Color_Green%                 SecondLlama Control Panel                                  %Color_Reset%
echo %Color_Cyan%================================================================================%Color_Reset%
echo.
echo %Color_Yellow%ASCII Art (Placeholder for SecondLlama branding if adapted later):%Color_Reset%
echo                                  ___________      ________          ________
echo                                  \__    ___/     /  _____/         /  _____/
echo                                    |    | ______/   \  ___  ______/   \  ___
echo                                    |    |/_____/\    \_\  \/_____/\    \_\  \
echo                                    |____|        \______  /        \______  /
echo                                                         \/                \/
echo.
echo %Color_Cyan%================================================================================%Color_Reset%
echo %Color_Green%Please choose an option:%Color_Reset%
echo.
echo %Color_Yellow%[1] Run SecondLlama%Color_Reset%
echo %Color_Yellow%[2] Run Installer/Update Dependencies%Color_Reset%
echo %Color_Yellow%[3] Exit%Color_Reset%
echo.
set /p "choice=Enter your choice (1, 2, or 3): "

if "%choice%"=="1" goto RunSecondLlama
if "%choice%"=="2" goto RunInstaller
if "%choice%"=="3" goto ExitScript
echo %Color_Red%Invalid choice. Please try again.%Color_Reset%
pause
goto MainMenu

REM --- Run SecondLlama ---
:RunSecondLlama
cls
echo %Color_Green%Starting SecondLlama...%Color_Reset%
echo.
echo %Color_Cyan%Attempting to activate virtual environment...%Color_Reset%
if exist ".\.venv\Scripts\activate.bat" (
    call ".\.venv\Scripts\activate.bat"
    echo %Color_Green%Virtual environment activated.%Color_Reset%
    echo.
    echo %Color_Cyan%Running launcher.py...%Color_Reset%
    python.exe -u ".\launcher.py"
    if errorlevel 1 (
        echo %Color_Red%Error running launcher.py. Please check the output above.%Color_Reset%
    ) else (
        echo %Color_Green%launcher.py finished.%Color_Reset%
    )
    echo.
    echo %Color_Cyan%Deactivating virtual environment...%Color_Reset%
    call ".\.venv\Scripts\deactivate.bat"
    echo %Color_Green%Virtual environment deactivated.%Color_Reset%
) else (
    echo %Color_Red%ERROR: Virtual environment not found at '.\.venv\Scripts\activate.bat'.%Color_Reset%
    echo %Color_Yellow%Please run the installer (Option 2) to set up the virtual environment.%Color_Reset%
)
echo.
echo %Color_Magenta%Press any key to return to the main menu...%Color_Reset%
pause >nul
goto MainMenu

REM --- Run Installer ---
:RunInstaller
cls
echo %Color_Green%Running Installer/Update Dependencies...%Color_Reset%
echo.
echo %Color_Cyan%The installer will create a virtual environment (if needed) and install/update packages.%Color_Reset%
echo %Color_Cyan%Attempting to activate virtual environment (if it exists, for consistency)...%Color_Reset%
if exist ".\.venv\Scripts\activate.bat" (
    call ".\.venv\Scripts\activate.bat"
    echo %Color_Green%Virtual environment activated for installer session.%Color_Reset%
) else (
    echo %Color_Yellow%Virtual environment not found or not yet created. The installer will handle this.%Color_Reset%
)
echo.
echo %Color_Cyan%Running installer.py...%Color_Reset%
python.exe ".\installer.py"
if errorlevel 1 (
    echo %Color_Red%Error running installer.py. Please check the output above.%Color_Reset%
) else (
    echo %Color_Green%installer.py finished.%Color_Reset%
    echo %Color_Yellow%If the installer created/updated the venv, you should be good to run SecondLlama.%Color_Reset%
)
echo.
echo %Color_Cyan%Deactivating virtual environment (if it was active)...%Color_Reset%
if defined VIRTUAL_ENV (
    call ".\.venv\Scripts\deactivate.bat"
    echo %Color_Green%Virtual environment deactivated.%Color_Reset%
) else (
    echo %Color_Yellow%Virtual environment was not active, no deactivation needed.%Color_Reset%
)
echo.
echo %Color_Magenta%Press any key to return to the main menu...%Color_Reset%
pause
goto MainMenu

REM --- Exit Script ---
:ExitScript
cls
echo %Color_Green%Exiting SecondLlama Control Panel. Goodbye!%Color_Reset%
timeout /t 2 /nobreak >nul
endlocal
exit /b

REM --- End of Script ---
