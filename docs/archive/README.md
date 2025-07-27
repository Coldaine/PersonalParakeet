# Documentation Archive

This directory contains historical and superseded documentation that has been consolidated into the main documentation structure.

## Structure

### `/v2/` - v2-Specific Documentation
Historical documentation related to the deprecated v2 (Tauri/WebSocket) architecture.

### `/migration/` - Migration Planning Documents  
Original migration plans and detailed feature tracking that have been superseded by the consolidated documentation.

### `/historical/` - Superseded Documentation
Status reports and documents that have been replaced by the unified documentation structure.

## Current Documentation

For up-to-date information, see the main documentation:
- [README.md](../README.md) - Project overview
- [ARCHITECTURE.md](../ARCHITECTURE.md) - Technical architecture  
- [DEVELOPMENT.md](../DEVELOPMENT.md) - Setup and development guide
- [STATUS.md](../STATUS.md) - Current progress and roadmap
- [TECHNICAL_REFERENCE.md](../TECHNICAL_REFERENCE.md) - Component specifications

## Archive Contents

| File | Original Location | Superseded By | Notes |
|------|------------------|---------------|-------|
| `v2/V2_HISTORICAL_CODE_ARCHIVE.md` | `/docs/` | N/A | Historical reference |
| `historical/LESSONS_AND_ANTI_PATTERNS.md` | `/docs/` | `ARCHITECTURE.md` | Key insights preserved |
| `historical/CURRENT_STATUS.md` | `/docs/` | `STATUS.md` | Outdated status |
| `historical/CURRENT_V3_STATUS.md` | `/v3-flet/docs/` | `STATUS.md` | Consolidated status |
| `migration/V3_ARCHITECTURE_AND_MIGRATION.md` | `/docs/` | `ARCHITECTURE.md` | Core decisions preserved |
| `migration/V3_FEATURE_MIGRATION_STATUS.md` | `/docs/` | `STATUS.md` | Simplified roadmap |
| `migration/KNOWLEDGE_BASE.md` | `/docs/` | `TECHNICAL_REFERENCE.md` | Patterns preserved |

## Restoration

If you need to restore any archived documentation:

```bash
# Example: Restore original migration plan
cp docs/archive/migration/V3_ARCHITECTURE_AND_MIGRATION.md docs/
```

**Note**: Archived documents may contain outdated information. Always check the current documentation first.