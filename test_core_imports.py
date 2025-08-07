try:
    import torch
    print("✅ PyTorch available")
    print(f"PyTorch version: {torch.__version__}")
except ImportError as e:
    print(f"❌ PyTorch not available: {e}")

try:
    import personalparakeet_ui
    print("✅ Rust UI module available")
except ImportError as e:
    print(f"❌ Rust UI module not available: {e}")

try:
    from personalparakeet.main import PersonalParakeetV3
    print("✅ Main application class available")
except ImportError as e:
    print(f"❌ Main application class not available: {e}")
