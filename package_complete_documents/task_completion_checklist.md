# Task Completion Checklist

When implementing features or fixing bugs:

1. **Code Quality**
   - Ensure code follows project conventions
   - Add appropriate error handling
   - Keep functions focused and modular

2. **Testing**
   - DO NOT automatically run tests
   - Tests should only be run when explicitly requested
   - Component tests are in test_components.py

3. **Documentation**
   - Update README.md if adding new features
   - Add docstrings to new classes/methods
   - Include usage examples for new functionality

4. **Dependencies**
   - Update requirements.txt if adding new packages
   - Specify version constraints for stability

5. **GPU Considerations**
   - Parakeet runs on GPU 0
   - Ollama runs on GPU 1
   - Include fallback to CPU if GPU unavailable

6. **User Experience**
   - Maintain responsive hotkeys
   - Provide clear status feedback
   - Handle errors gracefully without crashing