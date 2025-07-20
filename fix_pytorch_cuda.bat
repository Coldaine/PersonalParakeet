@echo off
echo Fixing PyTorch CUDA installation...
echo.

REM Uninstall CPU-only PyTorch
echo Removing CPU-only PyTorch...
.venv\Scripts\pip uninstall -y torch torchvision torchaudio

echo.
echo Installing PyTorch with CUDA support...
echo This will download ~2GB, please be patient...
echo.

REM Install PyTorch with CUDA 12.1 support
.venv\Scripts\pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

echo.
echo Testing installation...
.venv\Scripts\python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA version: {torch.version.cuda if torch.cuda.is_available() else \"N/A\"}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"

echo.
echo Done! You can now run: python start_workshop_box.py
pause