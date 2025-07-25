#!/usr/bin/env python3
"""
Test script for Clarity Engine integration
Tests the complete pipeline from raw STT to corrected output
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from personalparakeet.clarity_engine import ClarityEngine


async def test_clarity_engine():
    """Test the Clarity Engine with various inputs"""
    
    print("🧪 Testing Clarity Engine Integration")
    print("=" * 50)
    
    # Initialize engine
    engine = ClarityEngine(enable_rule_based=True)
    
    # Test initialization
    print("📋 Initializing Clarity Engine...")
    success = await engine.initialize()
    
    if not success:
        print("⚠️  LLM backend not available, testing rule-based corrections only")
    else:
        print("✅ Clarity Engine initialized successfully")
    
    # Start worker
    engine.start_worker()
    
    # Test cases that simulate real STT errors
    test_cases = [
        # Simple rule-based corrections
        "I need to go too the store",
        "Your going to love this new feature",
        "The weather is better then yesterday",
        
        # Technical jargon corrections
        "Please push this code to get hub",
        "I'm using pie torch for machine learning",
        "The react j s component is ready",
        "We need to setup the dock her container",
        "The my sequel database is running",
        
        # Mixed corrections (rules + potential LLM)
        "I think there going to use tensor flow for the gooey interface",
        "The colonel of the operating system needs updating",
        "We should commit this to get hub using the command line",
        
        # Complex sentences that might need LLM corrections
        "The quick brown fox jumps over the lazy dog",
        "I would like to schedule a meeting for next week to discuss the project timeline",
        
        # Edge cases
        "",
        "a",
        "This is a perfectly correct sentence with no errors."
    ]
    
    print("\n🔬 Testing Correction Pipeline")
    print("-" * 30)
    
    for i, test_text in enumerate(test_cases, 1):
        if not test_text.strip():
            continue
            
        print(f"\n{i}. Testing: '{test_text}'")
        
        # Test synchronous correction
        result = engine.correct_text_sync(test_text)
        
        print(f"   Original:  {result.original_text}")
        print(f"   Corrected: {result.corrected_text}")
        print(f"   Time:      {result.processing_time_ms:.1f}ms")
        print(f"   Confidence: {result.confidence:.2f}")
        
        if result.corrections_made:
            print(f"   Corrections: {result.corrections_made}")
        
        # Check if we're meeting our performance target
        if result.processing_time_ms > 150:
            print(f"   ⚠️  Slower than target (>150ms)")
        else:
            print(f"   ✅ Within target latency")
    
    # Performance summary
    stats = engine.get_performance_stats()
    print(f"\n📊 Performance Summary")
    print("-" * 30)
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    if stats['avg_processing_time_ms'] <= 150:
        print("✅ Average processing time meets target (<150ms)")
    else:
        print("⚠️  Average processing time exceeds target")
    
    # Stop worker
    engine.stop_worker()
    print("\n✅ Test completed successfully!")


async def test_websocket_integration():
    """Test integration with WebSocket bridge"""
    print("\n🌐 Testing WebSocket Integration")
    print("-" * 30)
    
    try:
        from workshop_websocket_bridge import WorkshopWebSocketBridge
        
        # Initialize bridge (this will create a Clarity Engine)
        bridge = WorkshopWebSocketBridge()
        
        # Test Clarity Engine initialization
        await bridge.initialize_clarity_engine()
        
        if bridge.clarity_engine.is_initialized:
            print("✅ WebSocket bridge Clarity Engine initialized")
        else:
            print("⚠️  WebSocket bridge Clarity Engine failed to initialize")
        
        # Test processing a sample transcription
        test_text = "I need to push this code to get hub using dock her"
        bridge.process_transcription(test_text)
        
        # Give it a moment to process
        await asyncio.sleep(1.0)
        
        print(f"✅ Successfully processed: '{test_text}'")
        print(f"   Current text: '{bridge.current_text}'")
        
    except Exception as e:
        print(f"❌ WebSocket integration test failed: {e}")


if __name__ == "__main__":
    async def main():
        await test_clarity_engine()
        await test_websocket_integration()
    
    asyncio.run(main())