@echo off
REM Garmin Companion - Asustor package build script
REM Usage:
REM   build.bat                 (bump patch: e.g. 1.0.0 -> 1.0.1)
REM   build.bat --bump minor    (bump minor: e.g. 1.0.0 -> 1.1.0)
REM   build.bat --bump major    (bump major: e.g. 1.0.0 -> 2.0.0)
REM   build.bat --version 1.2.0 (set the version)
REM   build.bat --no-bump       (keep the current version)

python "%~dp0build_package.py" %*
