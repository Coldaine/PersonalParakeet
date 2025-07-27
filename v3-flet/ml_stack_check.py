#!/usr/bin/env python3
"""
ML Stack Verification Script for PersonalParakeet v3
Checks CUDA, PyTorch, NeMo, and model availability
"""

import sys
import os
import subprocess
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class MLStackChecker:
    """Comprehensive ML stack verification"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = {}
        
    def check_python_version(self):
        """Check Python version compatibility"""
        logger.info("\n🐍 Checking Python version...")
        version = sys.version_info
        self.info['python_version'] = f"{version.major}.{version.minor}.{version.micro}"
        
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            self.errors.append(f"Python 3.8+ required, found {self.info['python_version']}")
        else:
            logger.info(f"  ✓ Python {self.info['python_version']}")
    
    def check_cuda(self):
        """Check CUDA availability and version"""
        logger.info("\n🎮 Checking CUDA...")
        
        # Check nvidia-smi
        try:
            result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("  ✓ nvidia-smi available")
                self.info['nvidia_smi'] = True
                
                # Extract CUDA version from nvidia-smi
                for line in result.stdout.split('\n'):
                    if 'CUDA Version' in line:
                        cuda_version = line.split('CUDA Version:')[1].strip().split()[0]
                        self.info['nvidia_smi_cuda'] = cuda_version
                        logger.info(f"  ✓ CUDA Version (driver): {cuda_version}")
            else:
                self.warnings.append("nvidia-smi not found - GPU may not be available")
                self.info['nvidia_smi'] = False
        except FileNotFoundError:
            self.warnings.append("nvidia-smi not found - NVIDIA driver not installed")
            self.info['nvidia_smi'] = False
    
    def check_pytorch(self):
        """Check PyTorch installation and CUDA support"""
        logger.info("\n🔥 Checking PyTorch...")
        
        try:
            import torch
            self.info['pytorch_version'] = torch.__version__
            logger.info(f"  ✓ PyTorch {torch.__version__}")
            
            # Check CUDA availability in PyTorch
            if torch.cuda.is_available():
                self.info['pytorch_cuda'] = True
                self.info['cuda_device_count'] = torch.cuda.device_count()
                self.info['cuda_device_name'] = torch.cuda.get_device_name(0)
                self.info['pytorch_cuda_version'] = torch.version.cuda
                
                logger.info(f"  ✓ CUDA available in PyTorch")
                logger.info(f"  ✓ CUDA version (PyTorch): {torch.version.cuda}")
                logger.info(f"  ✓ GPU devices: {torch.cuda.device_count()}")
                logger.info(f"  ✓ Primary GPU: {torch.cuda.get_device_name(0)}")
                
                # Check for RTX 5090 (requires special handling)
                if "5090" in torch.cuda.get_device_name(0):
                    self.warnings.append("RTX 5090 detected - may require PyTorch nightly for CUDA 12.8+ support")
                    logger.warning("  ⚠ RTX 5090 detected - special configuration may be needed")
                
                # Memory info
                memory_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
                logger.info(f"  ✓ GPU memory: {memory_gb:.1f} GB")
                
            else:
                self.info['pytorch_cuda'] = False
                self.warnings.append("CUDA not available in PyTorch - will use CPU (slower)")
                logger.warning("  ⚠ CUDA not available in PyTorch")
                
                # Check why CUDA might not be available
                if hasattr(torch.cuda, 'is_available'):
                    logger.info("  ℹ Checking CUDA diagnostics...")
                    try:
                        # This might provide more info
                        torch.cuda.init()
                    except Exception as e:
                        logger.info(f"    CUDA init error: {e}")
                        
        except ImportError:
            self.errors.append("PyTorch not installed - run: pip install torch")
            self.info['pytorch_version'] = None
            logger.error("  ✗ PyTorch not installed")
    
    def check_nemo(self):
        """Check NeMo toolkit installation"""
        logger.info("\n🎤 Checking NeMo...")
        
        try:
            import nemo
            self.info['nemo_version'] = nemo.__version__
            logger.info(f"  ✓ NeMo {nemo.__version__}")
            
            # Try importing ASR collections
            try:
                import nemo.collections.asr as nemo_asr
                logger.info("  ✓ NeMo ASR collections available")
                self.info['nemo_asr'] = True
            except ImportError as e:
                self.errors.append(f"NeMo ASR collections not available: {e}")
                self.info['nemo_asr'] = False
                
        except ImportError:
            self.errors.append("NeMo not installed - run: pip install nemo-toolkit[asr]")
            self.info['nemo_version'] = None
            logger.error("  ✗ NeMo not installed")
    
    def check_parakeet_model(self):
        """Check if Parakeet model can be loaded"""
        logger.info("\n🦜 Checking Parakeet model...")
        
        if not self.info.get('nemo_asr'):
            logger.warning("  ⚠ Skipping - NeMo ASR not available")
            return
            
        try:
            import torch
            import nemo.collections.asr as nemo_asr
            
            # Check local model file
            model_paths = [
                Path("models/parakeet-tdt-1.1b.nemo"),
                Path("v3-flet/models/parakeet-tdt-1.1b.nemo"),
                Path("../models/parakeet-tdt-1.1b.nemo"),
            ]
            
            local_model_found = False
            for model_path in model_paths:
                if model_path.exists():
                    logger.info(f"  ✓ Local model found: {model_path}")
                    self.info['local_model_path'] = str(model_path)
                    local_model_found = True
                    break
                    
            if not local_model_found:
                logger.info("  ℹ No local model found - will download from NGC on first use")
                
            # Try loading model (quick test)
            logger.info("  ℹ Testing model loading (this may take a moment)...")
            try:
                # Set to eval mode and use minimal memory
                with torch.inference_mode():
                    if local_model_found:
                        model = nemo_asr.models.ASRModel.restore_from(
                            str(self.info['local_model_path']),
                            map_location='cpu'  # Load to CPU first
                        )
                    else:
                        # This will download if not cached
                        model = nemo_asr.models.ASRModel.from_pretrained(
                            "nvidia/parakeet-tdt-1.1b",
                            map_location='cpu'
                        )
                    
                    logger.info("  ✓ Parakeet model loads successfully")
                    self.info['model_loadable'] = True
                    
                    # Cleanup
                    del model
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                        
            except Exception as e:
                self.warnings.append(f"Could not load Parakeet model: {str(e)}")
                logger.warning(f"  ⚠ Model loading test failed: {e}")
                self.info['model_loadable'] = False
                
        except Exception as e:
            self.errors.append(f"Model check failed: {e}")
            logger.error(f"  ✗ Model check error: {e}")
    
    def check_audio_libraries(self):
        """Check audio processing libraries"""
        logger.info("\n🔊 Checking audio libraries...")
        
        libraries = {
            'sounddevice': 'sounddevice',
            'numpy': 'numpy',
            'scipy': 'scipy',
            'soundfile': 'soundfile',
        }
        
        for name, module in libraries.items():
            try:
                lib = __import__(module)
                version = getattr(lib, '__version__', 'unknown')
                logger.info(f"  ✓ {name} {version}")
                self.info[f'{name}_version'] = version
            except ImportError:
                self.warnings.append(f"{name} not installed")
                logger.warning(f"  ⚠ {name} not installed")
    
    def check_stt_factory(self):
        """Test STT factory functionality"""
        logger.info("\n🏭 Checking STT Factory...")
        
        try:
            # Add parent directory to path
            sys.path.insert(0, str(Path(__file__).parent))
            
            from core.stt_factory import STTFactory
            
            # Check NeMo availability through factory
            nemo_available = STTFactory.check_nemo_availability()
            
            if nemo_available:
                logger.info("  ✓ STT Factory reports NeMo available")
            else:
                logger.info("  ⚠ STT Factory will use mock processor")
                
            # Get STT info
            stt_info = STTFactory.get_stt_info()
            logger.info(f"  ℹ STT Backend: {stt_info['backend']}")
            
            self.info['stt_factory_working'] = True
            
        except Exception as e:
            self.errors.append(f"STT Factory check failed: {e}")
            logger.error(f"  ✗ STT Factory error: {e}")
            self.info['stt_factory_working'] = False
    
    def generate_report(self):
        """Generate summary report"""
        logger.info("\n" + "="*60)
        logger.info("📊 ML STACK VERIFICATION SUMMARY")
        logger.info("="*60)
        
        # Overall status
        if self.errors:
            logger.error(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                logger.error(f"   • {error}")
        
        if self.warnings:
            logger.warning(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                logger.warning(f"   • {warning}")
        
        # Recommendations
        logger.info("\n💡 RECOMMENDATIONS:")
        
        if not self.info.get('pytorch_cuda'):
            logger.info("   • For GPU acceleration, install PyTorch with CUDA:")
            logger.info("     pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
            
        if not self.info.get('nemo_version'):
            logger.info("   • To enable real STT, install NeMo:")
            logger.info("     pip install nemo-toolkit[asr]")
            logger.info("     OR with Poetry: poetry install --with ml")
            
        if self.info.get('nvidia_smi') and "5090" in self.info.get('cuda_device_name', ''):
            logger.info("   • For RTX 5090 support, you may need PyTorch nightly:")
            logger.info("     pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu121")
        
        # Final status
        if not self.errors:
            if self.info.get('nemo_asr') and self.info.get('pytorch_cuda'):
                logger.info("\n✅ ML STACK READY - Full GPU acceleration available!")
            elif self.info.get('nemo_asr'):
                logger.info("\n✅ ML STACK READY - CPU mode (slower but functional)")
            else:
                logger.info("\n⚠️  ML STACK INCOMPLETE - Will use mock STT processor")
        else:
            logger.error("\n❌ ML STACK HAS ERRORS - Please fix the issues above")
        
        logger.info("\n" + "="*60)
    
    def run_all_checks(self):
        """Run all verification checks"""
        self.check_python_version()
        self.check_cuda()
        self.check_pytorch()
        self.check_nemo()
        self.check_parakeet_model()
        self.check_audio_libraries()
        self.check_stt_factory()
        self.generate_report()


def main():
    """Main entry point"""
    print("🚀 PersonalParakeet v3 - ML Stack Verification")
    print("="*60)
    
    checker = MLStackChecker()
    checker.run_all_checks()
    
    # Return exit code based on errors
    sys.exit(1 if checker.errors else 0)


if __name__ == "__main__":
    main()