# Virtual Environment Management for Parakeet Project

## Key Findings

1. **Tool Locations**:
   - `uv` and `uvx` are installed at: `~/.local/bin/`
   - These are NOT in the default PATH
   - Must use full path: `~/.local/bin/uvx`

2. **Virtual Environment**:
   - Located at: `/home/claude-user/parakeet/venv/`
   - Created with: `python3 -m venv venv`
   - Python version: 3.12

## Important Guidelines

### Working with Project Dependencies
```bash
# Always use this pattern for project-specific work:
source venv/bin/activate && <command>

# Examples:
source venv/bin/activate && pip install -r requirements.txt
source venv/bin/activate && python dictation.py
source venv/bin/activate && python automated_tests.py
```

### Working with System Tools
```bash
# For system-wide tools (uv, uvx, serena), use full paths:
~/.local/bin/uvx --from git+https://github.com/oraios/serena index-project /home/claude-user/parakeet

# Check system Python:
/usr/bin/python3 --version
```

## Best Practices

1. **Each Bash command runs in a new shell** - cannot use `deactivate`
2. **Always prefix venv commands** with `source venv/bin/activate &&`
3. **Use full paths** for tools in `~/.local/bin/`
4. **Project indexing** was completed with Serena

## Quick Reference

- **Run tests**: `source venv/bin/activate && python automated_tests.py`
- **Run app**: `source venv/bin/activate && python dictation.py`
- **Install deps**: `source venv/bin/activate && pip install -r requirements.txt`
- **Re-index**: `~/.local/bin/uvx --from git+https://github.com/oraios/serena index-project /home/claude-user/parakeet`