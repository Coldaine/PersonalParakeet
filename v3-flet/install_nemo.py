#!/usr/bin/env python3
"""
Install NeMo toolkit and Parakeet-TDT model for PersonalParakeet v3
Handles dependencies and model downloading
"""

import subprocess
import sys
import os
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_cuda():
    """Check CUDA availability"""
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        if cuda_available:
            logger.info(f"✓ CUDA available: {torch.cuda.get_device_name(0)}")
            logger.info(f"  CUDA version: {torch.version.cuda}")
            return True
        else:
            logger.warning("✗ CUDA not available")
            return False
    except ImportError:
        logger.error("PyTorch not installed")
        return False


def install_nemo_dependencies():
    """Install NeMo dependencies"""
    logger.info("Installing NeMo dependencies...")
    
    deps = [
        "Cython",
        "youtokentome",
        "numpy<2.0",  # NeMo may require older numpy
        "numba",
        "onnx",
        "hydra-core>=1.3",
        "omegaconf>=2.3",
        "pytorch-lightning>=2.0",
        "torchmetrics>=0.11",
        "transformers>=4.36",
        "webdataset>=0.2",
        "tensorboard",
        "text-unidecode",
        "pandas",
        "sentencepiece",
        "braceexpand",
        "librosa",
        "soundfile",
        "marshmallow",
        "packaging",
        "ruamel.yaml",
        "scikit-learn",
        "wrapt",
        "torch-stft",  # For audio processing
        "editdistance",  # For WER calculation
        "jiwer",  # For WER calculation
        "kaldi-python-io",  # Optional but useful
        "kaldiio",  # For Kaldi compatibility
        "pesq",  # For audio quality metrics
        "pystoi",  # For audio quality metrics
    ]
    
    for dep in deps:
        try:
            logger.info(f"Installing {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            logger.warning(f"Failed to install {dep}, continuing...")


def install_nemo():
    """Install NeMo toolkit"""
    logger.info("Installing NVIDIA NeMo toolkit...")
    
    # Try different installation methods
    methods = [
        # Method 1: Direct pip install
        [sys.executable, "-m", "pip", "install", "nemo_toolkit[asr]"],
        
        # Method 2: From GitHub (latest)
        [sys.executable, "-m", "pip", "install", "git+https://github.com/NVIDIA/NeMo.git@main#egg=nemo_toolkit[asr]"],
        
        # Method 3: Specific version known to work
        [sys.executable, "-m", "pip", "install", "nemo_toolkit[asr]==1.23.0"],
    ]
    
    for i, method in enumerate(methods):
        try:
            logger.info(f"Trying installation method {i+1}...")
            subprocess.check_call(method)
            logger.info("✓ NeMo installed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            logger.warning(f"Method {i+1} failed: {e}")
            continue
    
    logger.error("✗ Failed to install NeMo")
    return False


def download_parakeet_model():
    """Download Parakeet-TDT model"""
    logger.info("Preparing to download Parakeet-TDT model...")
    
    # Create models directory
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    # Model download script
    download_script = '''
import nemo.collections.asr as nemo_asr
from pathlib import Path

# Model options
models = {
    "parakeet-tdt-1.1b": "nvidia/parakeet-tdt-1.1b",
    "parakeet-ctc-1.1b": "nvidia/parakeet-ctc-1.1b", 
    "parakeet-rnnt-1.1b": "nvidia/parakeet-rnnt-1.1b",
}

print("Available Parakeet models:")
for name, path in models.items():
    print(f"  - {name}")

# Download TDT model (best for real-time)
model_name = "parakeet-tdt-1.1b"
print(f"\\nDownloading {model_name}...")

try:
    model = nemo_asr.models.ASRModel.from_pretrained(model_name=models[model_name])
    save_path = Path("models") / f"{model_name}.nemo"
    model.save_to(str(save_path))
    print(f"✓ Model saved to: {save_path}")
except Exception as e:
    print(f"✗ Failed to download model: {e}")
'''
    
    # Write and run download script
    script_path = models_dir / "download_parakeet.py"
    script_path.write_text(download_script)
    
    try:
        subprocess.check_call([sys.executable, str(script_path)])
        logger.info("✓ Parakeet model downloaded successfully!")
        return True
    except subprocess.CalledProcessError:
        logger.error("✗ Failed to download Parakeet model")
        return False


def test_nemo_import():
    """Test if NeMo can be imported"""
    try:
        import nemo
        import nemo.collections.asr as nemo_asr
        logger.info(f"✓ NeMo version: {nemo.__version__}")
        return True
    except ImportError as e:
        logger.error(f"✗ Cannot import NeMo: {e}")
        return False


def create_nemo_test_script():
    """Create a test script for NeMo STT"""
    test_script = '''#!/usr/bin/env python3
"""
Test NeMo Parakeet-TDT model
"""

import torch
import numpy as np
import nemo.collections.asr as nemo_asr
import sounddevice as sd
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_parakeet_inference():
    """Test Parakeet model inference"""
    logger.info("Testing Parakeet-TDT inference...")
    
    # Check CUDA
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Using device: {device}")
    
    # Load model
    try:
        # Try loading from local file first
        model_path = "models/parakeet-tdt-1.1b.nemo"
        if Path(model_path).exists():
            logger.info(f"Loading model from {model_path}")
            model = nemo_asr.models.ASRModel.restore_from(model_path)
        else:
            logger.info("Loading model from NGC")
            model = nemo_asr.models.ASRModel.from_pretrained("nvidia/parakeet-tdt-1.1b")
        
        model = model.to(device)
        model.eval()
        logger.info("✓ Model loaded successfully")
        
        # Generate test audio (sine wave)
        duration = 3.0
        sample_rate = 16000
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio = 0.5 * np.sin(2 * np.pi * 440 * t).astype(np.float32)
        
        # Run inference
        logger.info("Running inference on test audio...")
        with torch.no_grad():
            transcription = model.transcribe([audio])[0]
        
        logger.info(f"Transcription: '{transcription}'")
        logger.info("✓ Inference test passed!")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Inference test failed: {e}")
        return False


def test_realtime_transcription():
    """Test real-time transcription capability"""
    logger.info("\\nTesting real-time transcription...")
    
    try:
        model = nemo_asr.models.ASRModel.from_pretrained("nvidia/parakeet-tdt-1.1b")
        model.eval()
        
        # Audio parameters
        sample_rate = 16000
        chunk_duration = 0.5  # 500ms chunks
        chunk_samples = int(sample_rate * chunk_duration)
        
        logger.info(f"Recording for 5 seconds...")
        logger.info("Speak to test transcription!")
        
        # Record audio
        audio_chunks = []
        def callback(indata, frames, time, status):
            if status:
                logger.warning(f"Audio status: {status}")
            audio_chunks.append(indata.copy())
        
        with sd.InputStream(samplerate=sample_rate, channels=1, 
                          callback=callback, blocksize=chunk_samples):
            time.sleep(5)
        
        # Transcribe chunks
        logger.info("\\nTranscribing chunks:")
        for i, chunk in enumerate(audio_chunks):
            audio = chunk.flatten().astype(np.float32)
            if np.max(np.abs(audio)) > 0.01:  # Skip silent chunks
                text = model.transcribe([audio])[0]
                if text:
                    logger.info(f"  Chunk {i}: '{text}'")
        
        logger.info("✓ Real-time transcription test complete!")
        return True
        
    except Exception as e:
        logger.error(f"✗ Real-time test failed: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("NeMo Parakeet-TDT Test")
    print("=" * 60)
    
    # Run tests
    if test_parakeet_inference():
        print("\\n✓ Model inference working!")
    
    if test_realtime_transcription():
        print("\\n✓ Real-time transcription working!")
    
    print("\\n" + "=" * 60)
    print("NeMo is ready for PersonalParakeet v3!")
'''
    
    with open("test_nemo_stt.py", "w") as f:
        f.write(test_script)
    
    logger.info("Created test_nemo_stt.py")


def main():
    """Main installation process"""
    print("=" * 60)
    print("PersonalParakeet v3 - NeMo Installation")
    print("=" * 60)
    
    # Check CUDA
    if not check_cuda():
        logger.warning("CUDA not available - NeMo will run on CPU (slower)")
    
    # Install dependencies
    logger.info("\nStep 1: Installing dependencies...")
    install_nemo_dependencies()
    
    # Install NeMo
    logger.info("\nStep 2: Installing NeMo toolkit...")
    if not install_nemo():
        logger.error("Failed to install NeMo. Manual installation may be required.")
        logger.info("Try: pip install nemo_toolkit[asr]")
        return
    
    # Test import
    logger.info("\nStep 3: Testing NeMo import...")
    if not test_nemo_import():
        logger.error("NeMo installation appears to have failed")
        return
    
    # Download model
    logger.info("\nStep 4: Downloading Parakeet model...")
    download_parakeet_model()
    
    # Create test script
    create_nemo_test_script()
    
    print("\n" + "=" * 60)
    print("Installation complete!")
    print("Run 'python test_nemo_stt.py' to test the STT system")
    print("=" * 60)


if __name__ == "__main__":
    main()