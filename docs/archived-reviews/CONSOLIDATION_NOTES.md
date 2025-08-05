# Documentation Consolidation Notes

## Files Moved During Project Organization (August 2025)

### Analysis Files → docs/analysis/
- audio_engine_analysis.md
- code_blockers_analysis.md  
- project_review_analysis.md
- component_interaction_diagram.md
- detailed_component_diagrams.md
- system_architecture_diagram.md
- thought_linking_architecture_review.md
- thought_linking_implementation_gaps.md

### Review Files → docs/archived-reviews/
- final_project_review_report.md
- project_gap_filling_2025-08-03.md
- project_review_2025-08-03.md
- dependency_management_critique.md
- PERSONALPARAKEET_CLAIMS_VS_REALITY_COMPARISON.md
- DEPENDENCY_RESOLUTION_PLAN.md
- DEPENDENCY_SUMMARY.md
- FIX_DEPENDENCIES_NOW.md
- QUICK_FIX_INSTRUCTIONS.md
- rules.md

### Scripts → scripts/
- fix_ml_dependencies.sh, fix_nemo_install.sh, fix_rtx5090_poetry.sh
- clean_install_ml.sh, setup_ml_environment.sh
- install.sh, install.bat, activate.sh
- check_no_ml_in_poetry.sh, validate_environment.sh
- analyze_imports.py, check_dependencies.py, validate_environment.py, gpu_test.py
- launch.py, run_background.py
- import_analysis.json, test_config.yaml

### Test Files → tests/
- test_diagnostic_logs.py, test_main.py, test_dashboard.py
- test_stt_direct.py, test_stt_working.py

### Assets → tests/fixtures/audio/
- realtime_test.wav

### Removed
- python-evdev/ (external dependency that didn't belong in project)

## Documentation Status
- **SETUP.md**: RTX 5090-specific setup (keep separate from QUICKSTART.md)
- **SETUP_ML.md**: ML dependency management strategy (distinct from installation guide)
- **docs/QUICKSTART.md**: General quick start guide
- **docs/v3/ML_INSTALLATION_GUIDE.md**: Step-by-step ML installation

These files serve different purposes and should be maintained separately.