"""Allow running personalparakeet as a module: python -m personalparakeet"""

if __name__ == "__main__":
    try:
        from .dictation import main
        main()
    except ImportError as e:
        print(f"❌ Cannot run PersonalParakeet: Missing dependencies")
        print(f"   Error: {e}")
        print(f"   Install dependencies with: pip install -r requirements.txt")
        exit(1)