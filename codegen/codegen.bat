@echo off
setlocal enabledelayedexpansion

REM Variables
set VENV=.venv
set WORK_DIR=%~dp0

REM Change to the working directory
cd /d %WORK_DIR%

REM Activate the virtual environment
call ..\%VENV%\Scripts\activate.bat

REM Generate ORM code
if "%1" == "--run" (
    python codegen.py %1
) else (
    python codegen.py --help
    exit /b 1
)

REM Format files in the model directory
for %%f in (..\model\*.*) do (
    if not "%%~xf" == ".pyc" (
        echo Formatting file: %%f
        autopep8 -i ..\model\%%f
    )
)

REM Backup and clear new.SDL file
if exist new.model (
    move /y new.model new.model.bak
    type nul > new.model
)

echo Done!