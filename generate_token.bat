@echo off
REM Garmin Companion - Garmin Connect token generator
REM Usage:
REM   generate_token.bat                                (asks for credentials and 2FA, saves to .\garmin_tokens)
REM   generate_token.bat --upload http://NAS_IP:8095    (also uploads the token to the app)
REM   generate_token.bat --out C:\path\to\folder        (alternative output folder)

where python >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python is not installed or not on the PATH.
    echo Install it from https://www.python.org/downloads/ and tick "Add python.exe to PATH".
    pause
    exit /b 1
)

python -c "import garminconnect" >nul 2>nul
if errorlevel 1 (
    echo Installing garminconnect...
    python -m pip install --user "garminconnect>=0.3.2,<0.4"
    if errorlevel 1 (
        echo ERROR: could not install garminconnect.
        pause
        exit /b 1
    )
)

python "%~dp0generate_token.py" %*
pause
