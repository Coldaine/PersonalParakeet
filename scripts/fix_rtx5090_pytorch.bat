@echo off
echo ========================================
echo RTX 5090 PyTorch Compatibility Fix
echo ========================================
echo.
echo This will install PyTorch NIGHTLY build with RTX 5090 support
echo Based on: RTX 5090 CUDA Compatibility Solutions document
echo.

REM Uninstall existing PyTorch
echo Step 1: Removing existing PyTorch installation...
.venv\Scripts\pip uninstall -y torch torchvision torchaudio

echo.
echo Step 2: Installing PyTorch nightly build for RTX 5090 (Blackwell sm_120)...
echo This is the CRITICAL fix from the documentation!
echo.

REM Install PyTorch nightly with CUDA 12.8+ support for Blackwell
.venv\Scripts\pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128

echo.
echo Step 3: Verifying installation...
echo.

REM Test the installation
.venv\Scripts\python -c "import torch; print(f'PyTorch Version: {torch.__version__}'); print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'CUDA Version: {torch.version.cuda if torch.cuda.is_available() else \"N/A\"}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}'); print(f'Compute Capability: {torch.cuda.get_device_capability(0) if torch.cuda.is_available() else \"N/A\"}')"

echo.
echo ========================================
echo If you see Compute Capability: (12, 0) above, the fix worked!
echo You can now run: python start_workshop_box.py
echo ========================================
pause