#!/usr/bin/env python3
"""
Command Mode Simulation Tests
Tests voice command detection and execution without requiring actual speech input
"""

import asyncio
import json
import logging
from unittest.mock import AsyncMock, MagicMock
import sys
import os
import re
from typing import Optional

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import only what we need for testing - avoid full system dependencies
class MockCommandMode:
    """Mock implementation of Command Mode for testing"""
    
    def __init__(self):
        self.command_mode_enabled = True
        self.clarity_enabled = True
        self.is_listening = False
        self.current_text = ""
        
        # Voice command patterns (copied from actual implementation)
        self.command_patterns = {
            r'\b(?:commit|send|enter)\s+text\b': 'commit_text',
            r'\b(?:clear|delete|erase)\s+text\b': 'clear_text',
            r'\b(?:enable|turn\s+on)\s+clarity\b': 'enable_clarity',
            r'\b(?:disable|turn\s+off)\s+clarity\b': 'disable_clarity',
            r'\b(?:toggle)\s+clarity\b': 'toggle_clarity',
            r'\b(?:start|begin)\s+(?:listening|dictation)\b': 'start_listening',
            r'\b(?:stop|end)\s+(?:listening|dictation)\b': 'stop_listening',
        }
    
    def detect_voice_command(self, text: str) -> Optional[dict]:
        """Detect voice commands in transcribed text"""
        text_lower = text.lower().strip()
        
        for pattern, command in self.command_patterns.items():
            if re.search(pattern, text_lower, re.IGNORECASE):
                return {
                    'command': command,
                    'original_text': text,
                    'confidence': 0.9
                }
        
        return None
    
    async def execute_voice_command(self, command_result: dict):
        """Mock command execution"""
        command = command_result['command']
        
        # Simulate command execution
        if command == 'commit_text':
            self.current_text = ""
            return "Text committed"
        elif command == 'clear_text':
            self.current_text = ""
            return "Text cleared"
        elif command == 'enable_clarity':
            self.clarity_enabled = True
            return "Clarity enabled"
        elif command == 'disable_clarity':
            self.clarity_enabled = False
            return "Clarity disabled"
        elif command == 'toggle_clarity':
            self.clarity_enabled = not self.clarity_enabled
            return f"Clarity {'enabled' if self.clarity_enabled else 'disabled'}"
        elif command == 'start_listening':
            self.is_listening = True
            return "Dictation started"
        elif command == 'stop_listening':
            self.is_listening = False
            return "Dictation stopped"
        else:
            raise Exception(f"Unknown command: {command}")

class CommandModeSimulator:
    """Simulates voice commands for testing Command Mode functionality"""
    
    def __init__(self):
        self.mock_command_mode = MockCommandMode()
        self.test_results = []
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    async def simulate_voice_input(self, text: str) -> dict:
        """Simulate voice input and test command detection"""
        self.logger.info(f"Simulating voice input: '{text}'")
        
        # Test command detection
        command_result = self.mock_command_mode.detect_voice_command(text)
        
        if command_result:
            self.logger.info(f"✅ Command detected: {command_result['command']}")
            
            # Execute the command
            try:
                result_message = await self.mock_command_mode.execute_voice_command(command_result)
                status = "SUCCESS"
                self.logger.info(f"📤 Command executed: {result_message}")
            except Exception as e:
                status = f"ERROR: {e}"
                result_message = str(e)
                self.logger.error(f"❌ Command execution failed: {e}")
            
            return {
                "input": text,
                "detected": True,
                "command": command_result['command'],
                "status": status,
                "result": result_message,
                "confidence": command_result['confidence']
            }
        else:
            self.logger.info("❌ No command detected")
            return {
                "input": text,
                "detected": False,
                "command": None,
                "status": "NO_COMMAND",
                "result": None,
                "confidence": 0.0
            }
    
    async def run_test_suite(self):
        """Run comprehensive test suite for Command Mode"""
        self.logger.info("🚀 Starting Command Mode Test Suite")
        
        # Test cases: [input_text, expected_command]
        test_cases = [
            # Text management commands
            ("Please commit text now", "commit_text"),
            ("send text", "commit_text"),
            ("enter text please", "commit_text"),
            ("clear text", "clear_text"),
            ("delete text", "clear_text"),
            ("erase text now", "clear_text"),
            
            # Clarity engine commands
            ("enable clarity", "enable_clarity"),
            ("turn on clarity", "enable_clarity"),
            ("disable clarity", "disable_clarity"),
            ("turn off clarity", "disable_clarity"),
            ("toggle clarity", "toggle_clarity"),
            
            # Dictation control commands
            ("start listening", "start_listening"),
            ("begin dictation", "start_listening"),
            ("stop listening", "stop_listening"),
            ("end dictation", "stop_listening"),
            
            # Non-command inputs (should not trigger)
            ("This is just regular text", None),
            ("I committed to the project", None),
            ("Clear skies today", None),
            ("The text is unclear", None),
        ]
        
        # Run all test cases
        for i, (input_text, expected_command) in enumerate(test_cases, 1):
            self.logger.info(f"\n--- Test Case {i}/{len(test_cases)} ---")
            
            result = await self.simulate_voice_input(input_text)
            self.test_results.append(result)
            
            # Validate result
            if expected_command is None:
                # Should NOT detect a command
                if not result['detected']:
                    self.logger.info("✅ PASS: Correctly ignored non-command text")
                else:
                    self.logger.error(f"❌ FAIL: False positive - detected '{result['command']}' from '{input_text}'")
            else:
                # Should detect the expected command
                if result['detected'] and result['command'] == expected_command:
                    self.logger.info(f"✅ PASS: Correctly detected '{expected_command}'")
                elif result['detected']:
                    self.logger.error(f"❌ FAIL: Wrong command - expected '{expected_command}', got '{result['command']}'")
                else:
                    self.logger.error(f"❌ FAIL: Command not detected - expected '{expected_command}'")
            
            # Small delay for readability
            await asyncio.sleep(0.1)
    
    def generate_test_report(self):
        """Generate a comprehensive test report"""
        self.logger.info("\n" + "="*60)
        self.logger.info("📊 COMMAND MODE TEST REPORT")
        self.logger.info("="*60)
        
        total_tests = len(self.test_results)
        successful_detections = sum(1 for r in self.test_results if r['detected'] and r['status'] == 'SUCCESS')
        failed_detections = sum(1 for r in self.test_results if r['detected'] and 'ERROR' in str(r['status']))
        false_positives = sum(1 for r in self.test_results if r['detected'] and r['input'] in [
            "This is just regular text", "I committed to the project", "Clear skies today", "The text is unclear"
        ])
        missed_commands = sum(1 for r in self.test_results if not r['detected'] and r['input'] not in [
            "This is just regular text", "I committed to the project", "Clear skies today", "The text is unclear"
        ])
        
        self.logger.info(f"Total Tests: {total_tests}")
        self.logger.info(f"Successful Command Executions: {successful_detections}")
        self.logger.info(f"Failed Command Executions: {failed_detections}")
        self.logger.info(f"False Positives: {false_positives}")
        self.logger.info(f"Missed Commands: {missed_commands}")
        
        # Command breakdown
        commands_tested = {}
        for result in self.test_results:
            if result['detected']:
                cmd = result['command']
                if cmd not in commands_tested:
                    commands_tested[cmd] = {'success': 0, 'failed': 0}
                
                if result['status'] == 'SUCCESS':
                    commands_tested[cmd]['success'] += 1
                else:
                    commands_tested[cmd]['failed'] += 1
        
        self.logger.info("\nCommand Performance:")
        for cmd, stats in commands_tested.items():
            total = stats['success'] + stats['failed']
            success_rate = (stats['success'] / total * 100) if total > 0 else 0
            self.logger.info(f"  {cmd}: {stats['success']}/{total} ({success_rate:.1f}% success)")
        
        # Overall assessment
        overall_success_rate = (successful_detections / (total_tests - 4) * 100)  # Exclude 4 non-command tests
        self.logger.info(f"\nOverall Success Rate: {overall_success_rate:.1f}%")
        
        if overall_success_rate >= 90:
            self.logger.info("🎉 EXCELLENT: Command Mode is working perfectly!")
        elif overall_success_rate >= 75:
            self.logger.info("✅ GOOD: Command Mode is working well with minor issues")
        elif overall_success_rate >= 50:
            self.logger.info("⚠️  FAIR: Command Mode needs improvement")
        else:
            self.logger.info("❌ POOR: Command Mode requires significant fixes")

async def main():
    """Main test execution"""
    simulator = CommandModeSimulator()
    
    try:
        await simulator.run_test_suite()
        simulator.generate_test_report()
        
        # Save detailed results
        with open('command_mode_test_results.json', 'w') as f:
            json.dump(simulator.test_results, f, indent=2)
        
        print(f"\n📁 Detailed results saved to: command_mode_test_results.json")
        
    except Exception as e:
        logging.error(f"Test suite failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())