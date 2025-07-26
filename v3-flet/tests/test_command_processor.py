#!/usr/bin/env python3
"""
Test for Command Processor functionality
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from core.command_processor import CommandProcessor, create_command_processor


def test_command_processor():
    """Test basic command processor functionality"""
    print("Testing Command Processor...")
    
    # Create command processor
    processor = create_command_processor(activation_phrase="hey parakeet")
    
    # Test activation phrase detection
    activation_result = processor.process_speech("hey parakeet")
    print(f"Activation result: {activation_result}")
    
    # Test command detection (should work after activation)
    if activation_result:
        command_result = processor.process_speech("clear text")
        print(f"Command result: {command_result}")
    
    # Test state info
    state_info = processor.get_state_info()
    print(f"State info: {state_info}")
    
    print("Command Processor test completed!")


if __name__ == "__main__":
    test_command_processor()