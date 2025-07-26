"""Allow running personalparakeet as a module: python -m personalparakeet"""

if __name__ == "__main__":
    try:
        from .dictation import main
        main()
    except ImportError as e:
        # Print to stderr for startup errors before logging is available
        import sys
        sys.stderr.write(f"❌ Cannot run PersonalParakeet: Missing dependencies\n")
        sys.stderr.write(f"   Error: {e}\n")
        sys.stderr.write(f"   Install dependencies with: pip install -r requirements.txt\n")
        exit(1)