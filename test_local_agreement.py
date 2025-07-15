#!/usr/bin/env python3
"""
Test LocalAgreement algorithm to understand why it's not working
with streaming audio chunks
"""

from ESSENTIAL_LocalAgreement_Code import TranscriptionProcessor

def test_streaming_scenario():
    """Simulate what happens with streaming audio chunks"""
    print("🧪 Testing LocalAgreement with Streaming Audio Simulation")
    print("=" * 60)
    
    processor = TranscriptionProcessor(agreement_threshold=2, enable_visual_feedback=False)
    
    # Track when text gets committed
    committed_texts = []
    def capture_committed_text(text):
        committed_texts.append(text)
        print(f"🎯 COMMITTED: '{text}'")
    
    processor.set_text_output_callback(capture_committed_text)
    
    # Simulate streaming transcriptions (what we saw in the log)
    streaming_transcriptions = [
        "no",
        "hope", 
        "his works",
        "",  # Empty transcription
        "eh i i feel like",
        "maybe there's",
        "this is the chunking is happening to",
        "too quickly or something",
        "",  # Empty transcription
        "and",
        "none of the text is actually coming out"
    ]
    
    print("Simulating streaming transcriptions:")
    print("-" * 40)
    
    for i, transcription in enumerate(streaming_transcriptions):
        print(f"\nChunk {i+1}: '{transcription}'")
        state = processor.process_transcription(transcription)
        
        # Show the internal state
        print(f"  Committed: '{state.committed}'")
        print(f"  Pending: '{state.pending}'")
        print(f"  Newly committed: '{state.newly_committed}'")
        
        # Show word agreements for debugging
        if processor.buffer.word_agreements:
            print("  Word agreements:")
            for pos, word_counts in processor.buffer.word_agreements.items():
                for word, count in word_counts.items():
                    print(f"    Position {pos}: '{word}' = {count} agreements")
    
    print(f"\n📊 Final Results:")
    print(f"Total committed texts: {len(committed_texts)}")
    print(f"Committed texts: {committed_texts}")
    print(f"Final committed text: '{processor.buffer.committed_text}'")
    print(f"Final pending text: '{' '.join(processor.buffer.pending_words)}'")

def test_ideal_scenario():
    """Test how LocalAgreement should work with repeated transcriptions"""
    print("\n\n🧪 Testing LocalAgreement with Ideal Repeated Transcriptions")
    print("=" * 60)
    
    processor = TranscriptionProcessor(agreement_threshold=2, enable_visual_feedback=False)
    
    committed_texts = []
    def capture_committed_text(text):
        committed_texts.append(text)
        print(f"🎯 COMMITTED: '{text}'")
    
    processor.set_text_output_callback(capture_committed_text)
    
    # Simulate ideal scenario - same transcription repeated
    ideal_transcriptions = [
        "hello world this is working",
        "hello world this is working", 
        "hello world this is working great",
        "hello world this is working great",
        "hello world this is working great now",
        "hello world this is working great now"
    ]
    
    print("Simulating ideal repeated transcriptions:")
    print("-" * 40)
    
    for i, transcription in enumerate(ideal_transcriptions):
        print(f"\nTranscription {i+1}: '{transcription}'")
        state = processor.process_transcription(transcription)
        
        print(f"  Committed: '{state.committed}'")
        print(f"  Pending: '{state.pending}'")
        print(f"  Newly committed: '{state.newly_committed}'")
    
    print(f"\n📊 Final Results:")
    print(f"Total committed texts: {len(committed_texts)}")
    print(f"Committed texts: {committed_texts}")

def test_overlapping_chunks():
    """Test a potential solution with overlapping chunks"""
    print("\n\n🧪 Testing Potential Solution: Overlapping Chunks")
    print("=" * 60)
    
    processor = TranscriptionProcessor(agreement_threshold=2, enable_visual_feedback=False)
    
    committed_texts = []
    def capture_committed_text(text):
        committed_texts.append(text)
        print(f"🎯 COMMITTED: '{text}'")
    
    processor.set_text_output_callback(capture_committed_text)
    
    # Simulate overlapping chunks that might give words more chances
    overlapping_transcriptions = [
        "hello world",
        "hello world this",
        "world this is", 
        "this is working",
        "is working great",
        "working great now"
    ]
    
    print("Simulating overlapping chunk transcriptions:")
    print("-" * 40)
    
    for i, transcription in enumerate(overlapping_transcriptions):
        print(f"\nChunk {i+1}: '{transcription}'")
        state = processor.process_transcription(transcription)
        
        print(f"  Committed: '{state.committed}'")
        print(f"  Pending: '{state.pending}'")
        print(f"  Newly committed: '{state.newly_committed}'")
    
    print(f"\n📊 Final Results:")
    print(f"Total committed texts: {len(committed_texts)}")
    print(f"Committed texts: {committed_texts}")

if __name__ == "__main__":
    test_streaming_scenario()
    test_ideal_scenario() 
    test_overlapping_chunks()