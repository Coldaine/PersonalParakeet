#!/usr/bin/env python3
"""
Run the enhanced PersonalParakeet dictation system with improved error handling

This version includes:
- Audio device selection
- Improved cleanup handling  
- Better error recovery
- Fallback text display
"""

from personalparakeet.dictation import cli

if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════╗
║         PersonalParakeet Enhanced Dictation System         ║
║                                                            ║
║  Features:                                                 ║
║  ✅ Audio device selection (--device or --device-name)    ║
║  ✅ Improved text output with thread safety               ║
║  ✅ Enhanced error handling and recovery                  ║
║  ✅ Fallback console display when injection fails         ║
║  ✅ Better audio processing with error limits             ║
║  ✅ Graceful shutdown and cleanup                         ║
║  ✅ Signal handling (Ctrl+C, SIGTERM)                     ║
║                                                            ║
║  Version: 2.1 (Enhanced with device selection)             ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Run the main dictation system with CLI support
    cli()