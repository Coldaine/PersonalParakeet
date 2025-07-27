@echo off
REM PersonalParakeet v3 - Hybrid Installation Script for Windows
REM Uses Poetry for Python deps and Conda for ML/CUDA deps

echo.
echo 🦜 PersonalParakeet v3 - Hybrid Installation (Windows)
echo =====================================================
echo.

REM Check for Poetry
where poetry >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Poetry is not installed. Please install Poetry first.
    echo    Visit: https://python-poetry.org/docs/#installation
    exit /b 1
)

REM Check for Conda
where conda >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Conda is not installed. Please install Miniconda or Anaconda first.
    echo    Visit: https://docs.conda.io/en/latest/miniconda.html
    exit /b 1
)

echo ✅ Prerequisites found
echo.

REM Ask for installation type
echo 🤔 Choose installation type:
echo 1) Full installation (with ML/CUDA support)
echo 2) Base installation (mock STT only)
echo.
set /p choice="Enter choice (1 or 2): "

REM Step 1: Install Python dependencies with Poetry
echo.
echo 📦 Installing Python dependencies with Poetry...
poetry install
if %errorlevel% neq 0 (
    echo ❌ Poetry install failed
    exit /b 1
)

REM Step 2: Handle ML dependencies based on choice
if "%choice%"=="1" (
    echo.
    echo 🧠 Setting up ML environment with Conda...
    
    REM Create/update conda environment
    echo Creating conda environment 'personalparakeet'...
    conda env create -f environment.yml -n personalparakeet 2>nul || conda env update -f environment.yml -n personalparakeet
    
    echo.
    echo ✅ Full installation complete!
    echo.
    echo 🚀 To use PersonalParakeet with ML support:
    echo    1. Activate Poetry shell: poetry shell
    echo    2. Activate Conda env: conda activate personalparakeet
    echo    3. Run: python main.py
    echo.
    echo 📝 Don't forget to update config.json:
    echo    Set "use_mock_stt": false for real STT
) else (
    echo.
    echo ✅ Base installation complete!
    echo.
    echo 🚀 To use PersonalParakeet with mock STT:
    echo    1. Activate Poetry shell: poetry shell
    echo    2. Run: python main.py
    echo.
    echo 📝 config.json is already set to use mock STT
)

echo.
echo 📚 For more information, see docs\ML_INSTALLATION_GUIDE.md
echo 🦜 Happy dictating!
pause