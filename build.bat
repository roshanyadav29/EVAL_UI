@echo off
echo HYDRA GUI Build Script
echo =====================

REM Change to build_tools directory
cd /d "%~dp0build_tools"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if build_exe.py exists
if not exist "build_exe.py" (
    echo Error: build_exe.py not found
    echo Please ensure you're running this from the project root
    pause
    exit /b 1
)

REM Run the build script
echo Running build process...
python build_exe.py

REM Check if build was successful
if errorlevel 1 (
    echo Build failed! Check the error messages above.
) else (
    echo Build completed! Check the dist folder for your executable.
)

echo.
echo Press any key to continue...
pause >nul
