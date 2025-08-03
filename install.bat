@echo off
REM PersonalParakeet v3 - Simple Installation Script for Windows

echo PersonalParakeet v3 Installation
echo ==================================
echo.

REM Check if conda is installed
where conda >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Conda is not installed!
    echo Please install Miniconda from: https://docs.conda.io/en/latest/miniconda.html
    exit /b 1
)

echo Conda found
echo.

REM Remove existing environment if it exists
echo Checking for existing environment...
conda env list | findstr "personalparakeet" >nul 2>nul
if %errorlevel% equ 0 (
    echo Found existing environment. Removing...
    conda env remove -n personalparakeet -y
)

REM Create new environment
echo Creating conda environment with all dependencies...
echo This will install PyTorch, CUDA, and all required packages.
echo.

conda env create -f environment-complete.yml

if %errorlevel% equ 0 (
    echo.
    echo Installation complete!
    echo.
    echo To run PersonalParakeet:
    echo   1. conda activate personalparakeet
    echo   2. python -m personalparakeet
    echo.
) else (
    echo.
    echo Installation failed!
    echo Please check the error messages above.
    exit /b 1
)