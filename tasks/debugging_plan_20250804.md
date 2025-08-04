# PersonalParakeet Debugging Plan - Dual Agent Approach
## Date: August 4, 2025

## ONE-SHOT INSTRUCTIONS

### For Agent A:
```
@tasks/debugging_plan_20250804.md

You are Agent A. Your role: Systematic debugging. Create findings at /tasks/agent_a_findings.md

Phase 1: Debug these issues IN ORDER:
1. Test discovery failure (0 tests found)
2. GPU memory reporting (shows 0MB)
3. Missing logging

Execute all commands under "AGENT A TASKS" section. Document every command and output.

Phase 2: After completing Phase 1, read /tasks/agent_b_findings.md and add cross-review section to your findings.

Start now with Phase 1.
```

### For Agent B:
```
@tasks/debugging_plan_20250804.md

You are Agent B. Your role: Creative debugging. Create findings at /tasks/agent_b_findings.md

Phase 1: Attack these issues CREATIVELY:
1. GPU memory reporting (shows 0MB) - start here
2. Test discovery failure (0 tests found) - try unconventional approaches
3. Quick logging implementation

Execute all commands under "AGENT B TASKS" section. Try experimental solutions.

Phase 2: After completing Phase 1, read /tasks/agent_a_findings.md and add cross-review section to your findings.

Start now with Phase 1.
```

---

## AGENT A TASKS

Execute these commands in order and document results:

```bash
# 1. Environment verification
conda activate personalparakeet
poetry run python -c "import personalparakeet; print('Import OK')"
poetry run pytest --version

# 2. Test discovery debugging
poetry run pytest --collect-only
poetry run pytest tests/ -v
find tests/ -name "test_*.py" | head -10
poetry run python -c "import tests.hardware.test_gpu_cuda"
poetry show | grep pytest
poetry run python -m pytest tests/ --tb=short

# 3. GPU investigation
poetry run python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
nvidia-smi
poetry run python -c "import torch; x=torch.randn(1000,1000).cuda() if torch.cuda.is_available() else None; print(f'GPU mem: {torch.cuda.memory_allocated()/1024**2:.1f}MB' if torch.cuda.is_available() else 'No CUDA')"

# 4. Document findings in /tasks/agent_a_findings.md with this structure:
# - Test Discovery: [what failed, why, solution]
# - GPU Detection: [current state, root cause]
# - Recommendations: [ordered list of fixes]
```

---

## AGENT B TASKS

Execute these creative approaches and document results:

```bash
# 1. GPU creative debugging (START HERE)
conda activate personalparakeet
poetry run python tests/hardware/test_gpu_cuda.py

# Create custom GPU memory test
cat > gpu_test.py << 'EOF'
import torch
try:
    import nvidia_ml_py3 as pynvml
    pynvml.nvmlInit()
    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
    info = pynvml.nvmlDeviceGetMemoryInfo(handle)
    print(f"NVML GPU Memory: {info.used/1024**2:.0f}MB used")
except ImportError:
    print("nvidia-ml-py3 not installed")
except Exception as e:
    print(f"NVML error: {e}")

if torch.cuda.is_available():
    torch.cuda.init()
    print(f"PyTorch sees GPU: {torch.cuda.get_device_name(0)}")
    tensor = torch.randn(2000, 2000).cuda()
    print(f"PyTorch GPU memory after allocation: {torch.cuda.memory_allocated()/1024**2:.1f}MB")
else:
    print("CUDA not available to PyTorch")
EOF
poetry run python gpu_test.py

# 2. Alternative test discovery
cd tests && poetry run python -m pytest && cd ..
PYTHONPATH=. poetry run pytest
poetry run python -m pytest hardware/test_audio_capture.py::TestAudioCapture -v

# 3. Quick fixes
poetry run pip install -r requirements-torch.txt
poetry cache clear --all .
rm -rf .pytest_cache
poetry run pytest --cache-clear

# 4. Add quick logging
mkdir -p logs
echo "import logging; logging.basicConfig(filename='logs/debug.log', level=logging.DEBUG)" > src/personalparakeet/quick_log.py

# 5. Document findings in /tasks/agent_b_findings.md with this structure:
# - GPU Discovery: [creative solutions that worked]
# - Test Workarounds: [alternative approaches]
# - Unexpected Findings: [anything surprising]
```

---

## PHASE 2 TEMPLATE

After Phase 1, add this to your findings file:

```markdown
## Phase 2: Cross-Review of Agent [A/B]'s Findings

### Key discoveries they made:
- [What the other agent found]

### Where we disagree:
- [Any contradictions]

### Combined solution:
1. [Best fix for tests]
2. [Best fix for GPU]
3. [Best fix for logging]

### Final recommendation:
[The one approach that definitely works]
```

---

## CONTEXT: The Three Issues

1. **Test Discovery Broken**: `poetry run pytest` finds 0 tests (was finding 3)
2. **GPU Memory Always 0MB**: Even when GPU is being used for STT
3. **No Application Logs**: Can't debug runtime issues

## Success Looks Like

- Tests: 10+ tests discovered and passing
- GPU: Real memory usage shown (>0MB during STT operations)
- Logs: debug.log file created with useful output
- Both agents have findings files with cross-review sections