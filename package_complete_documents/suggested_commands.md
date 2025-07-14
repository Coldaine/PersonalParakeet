# Suggested Commands for Development

## Installation
```bash
pip install -r requirements.txt
```

## Running the Application
```bash
python dictation.py
```

## Testing Components (DO NOT RUN AUTOMATICALLY)
```bash
# Manual testing only when explicitly requested
pytest test_components.py
```

## System Commands (Linux)
- `ls -la` - List files with details
- `cd <directory>` - Change directory
- `pwd` - Print working directory
- `cat <file>` - View file contents
- `grep -r "pattern" .` - Search for pattern in files
- `find . -name "*.py"` - Find Python files

## Git Commands
- `git status` - Check repository status
- `git add .` - Stage all changes
- `git commit -m "message"` - Commit changes
- `git log --oneline` - View commit history

## Python Development
- `python -m venv venv` - Create virtual environment
- `source venv/bin/activate` - Activate virtual environment (Linux)
- `pip freeze > requirements.txt` - Update requirements

## GPU Monitoring
- `nvidia-smi` - Check GPU status and memory usage
- `watch -n 1 nvidia-smi` - Monitor GPU in real-time