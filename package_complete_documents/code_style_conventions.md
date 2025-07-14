# Code Style and Conventions

## Python Style Guide
- Use Python 3.x syntax and features
- Follow PEP 8 naming conventions:
  - Classes: PascalCase (e.g., `AudioHandler`, `StreamingParakeet`)
  - Functions/methods: snake_case (e.g., `process_audio`, `get_speech_chunk`)
  - Constants: UPPER_CASE
  - Private methods: prefix with underscore (e.g., `_find_best_device`)

## Type Hints
- Use type hints for function parameters and returns where beneficial
- Example: `async def refine_text(self, text: str, context_type: str = "general") -> str:`

## Docstrings
- Use concise docstrings for classes and important methods
- Triple quotes for multi-line docstrings
- Brief description of purpose and functionality

## Code Organization
- Group related imports together (standard library, third-party, local)
- Class methods organized logically: `__init__`, public methods, private methods
- Use descriptive variable names
- Keep functions focused on single responsibility

## Error Handling
- Use try-except blocks for external operations (audio, network, file I/O)
- Graceful degradation when optional features fail
- Print informative error messages for debugging

## Comments
- Use inline comments sparingly for complex logic
- Prefer self-documenting code with clear naming
- Add section comments to separate major code blocks