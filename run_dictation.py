#!/usr/bin/env python3
"""Main entry point for PersonalParakeet dictation system

This is the simple, working dictation system as documented in CLAUDE.md
"""

import sys
from personalparakeet.dictation import main

if __name__ == "__main__":
    sys.exit(main())