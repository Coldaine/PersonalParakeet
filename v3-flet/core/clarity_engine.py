#!/usr/bin/env python3
"""
Clarity Engine - Direct port from personalparakeet.clarity_engine
Real-time text correction engine with rule-based corrections
"""

import asyncio
import logging
import time
import re
from typing import Optional, List, Tuple, Callable
from dataclasses import dataclass
import threading
import queue


@dataclass
class CorrectionResult:
    """Result of text correction"""
    original_text: str
    corrected_text: str
    confidence: float
    processing_time_ms: float
    corrections_made: List[Tuple[str, str]]  # [(original, corrected), ...]


class ClarityEngine:
    """
    Real-time text correction engine with rule-based corrections
    Designed for <50ms latency with rule-based corrections only
    """
    
    def __init__(self, enable_rule_based: bool = True):
        self.enable_rule_based = enable_rule_based
        
        # State
        self.is_initialized = True  # Rule-based is always ready
        self.context_buffer = []
        
        # Performance tracking
        self.correction_count = 0
        self.total_processing_time = 0.0
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize correction queue for async processing
        self.correction_queue = queue.Queue()
        self.worker_thread = None
        self.is_running = False
        
        # Rule-based corrections (essential tech terms only)
        self.jargon_corrections = {
            "clod code": "claude code",
            "cloud code": "claude code",
            "get hub": "github",
            "pie torch": "pytorch", 
            "dock her": "docker",
            "colonel": "kernel"
        }
    
    async def initialize(self) -> bool:
        """Initialize - always succeeds for rule-based mode"""
        self.logger.info("Clarity Engine initialized in rule-based mode")
        return True
    
    def start_worker(self):
        """Start the background correction worker thread"""
        if self.worker_thread is None or not self.worker_thread.is_alive():
            self.is_running = True
            self.worker_thread = threading.Thread(target=self._correction_worker, daemon=True)
            self.worker_thread.start()
            self.logger.info("Clarity Engine worker thread started")
    
    def stop_worker(self):
        """Stop the background correction worker thread"""
        self.is_running = False
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=2.0)
            self.logger.info("Clarity Engine worker thread stopped")
    
    def _correction_worker(self):
        """Background worker for processing corrections"""
        while self.is_running:
            try:
                # Get correction task from queue (blocking with timeout)
                task = self.correction_queue.get(timeout=1.0)
                if task is None:
                    continue
                
                text, callback = task
                result = self._process_correction_sync(text)
                
                # Call the callback with result
                if callback:
                    callback(result)
                
                self.correction_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error in correction worker: {e}")
    
    def correct_text_async(self, text: str, callback: Optional[Callable[[CorrectionResult], None]] = None):
        """Queue text for asynchronous correction"""
        if not self.is_running:
            self.start_worker()
        
        # Add to correction queue
        self.correction_queue.put((text, callback))
    
    def correct_text_sync(self, text: str) -> CorrectionResult:
        """Synchronously correct text (blocks until complete)"""
        return self._process_correction_sync(text)
    
    def _process_correction_sync(self, text: str) -> CorrectionResult:
        """Internal method to process corrections synchronously"""
        start_time = time.time()
        corrections_made = []
        
        # Apply rule-based corrections
        corrected_text = text
        if self.enable_rule_based:
            corrected_text, rule_corrections = self._apply_rule_based_corrections(corrected_text)
            corrections_made.extend(rule_corrections)
        
        processing_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Update stats
        self.correction_count += 1
        self.total_processing_time += processing_time
        
        # Calculate confidence based on number of corrections
        confidence = 0.9 if len(corrections_made) > 0 else 0.8
        
        result = CorrectionResult(
            original_text=text,
            corrected_text=corrected_text,
            confidence=confidence,
            processing_time_ms=processing_time,
            corrections_made=corrections_made
        )
        
        return result
    
    def _apply_rule_based_corrections(self, text: str) -> Tuple[str, List[Tuple[str, str]]]:
        """Apply fast rule-based corrections"""
        corrections = []
        corrected_text = text
        
        # Apply jargon corrections (case-insensitive)
        for incorrect, correct in self.jargon_corrections.items():
            if incorrect.lower() in corrected_text.lower():
                pattern = re.compile(re.escape(incorrect), re.IGNORECASE)
                if pattern.search(corrected_text):
                    corrected_text = pattern.sub(correct, corrected_text)
                    corrections.append((incorrect, correct))
        
        # Apply homophone corrections (context-aware)
        words = corrected_text.split()
        corrected_words = []
        
        for i, word in enumerate(words):
            clean_word = word.strip('.,!?;:"()[]{}').lower()
            corrected_word = word
            
            # Context-aware homophone corrections
            if clean_word == "too" and i + 1 < len(words):
                next_word = words[i + 1].lower()
                if next_word in ["the", "a", "an", "this", "that", "school", "work", "home"]:
                    # "too the store" -> "to the store"
                    corrected_word = word.replace("too", "to").replace("Too", "To")
                    corrections.append(("too", "to"))
            elif clean_word == "your" and i + 1 < len(words):
                next_word = words[i + 1].lower()
                if next_word in ["going", "coming", "looking", "getting", "doing", "working"]:
                    # "your going" -> "you're going"
                    corrected_word = word.replace("your", "you're").replace("Your", "You're")
                    corrections.append(("your", "you're"))
            elif clean_word == "there" and i + 1 < len(words):
                next_word = words[i + 1].lower()
                if next_word in ["going", "coming", "doing"]:
                    # "there going" -> "they're going"
                    corrected_word = word.replace("there", "they're").replace("There", "They're")
                    corrections.append(("there", "they're"))
                elif next_word in ["house", "car", "phone", "computer", "job"]:
                    # "there house" -> "their house"
                    corrected_word = word.replace("there", "their").replace("There", "Their")
                    corrections.append(("there", "their"))
            elif clean_word == "its" and i + 1 < len(words):
                next_word = words[i + 1].lower()
                if next_word in ["going", "time", "ready", "working"]:
                    # "its going" -> "it's going"
                    corrected_word = word.replace("its", "it's").replace("Its", "It's")
                    corrections.append(("its", "it's"))
            
            corrected_words.append(corrected_word)
        
        final_text = ' '.join(corrected_words)
        return final_text, corrections
    
    def get_performance_stats(self) -> dict:
        """Get performance statistics"""
        avg_time = self.total_processing_time / max(self.correction_count, 1)
        return {
            'total_corrections': self.correction_count,
            'avg_processing_time_ms': avg_time,
            'target_latency_ms': 50,  # Rule-based target
            'performance_ratio': avg_time / 50,
            'backend': 'rule-based',
            'initialized': self.is_initialized
        }
    
    def update_context(self, text: str):
        """Update the context buffer"""
        self.context_buffer.append(text)
        
        # Keep only recent context
        if len(self.context_buffer) > 10:
            self.context_buffer.pop(0)
    
    def clear_context(self):
        """Clear the context buffer"""
        self.context_buffer.clear()