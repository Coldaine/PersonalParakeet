#!/usr/bin/env python3
"""
Thought Linking Integration - PLACEHOLDER IMPLEMENTATION (NOT ACTIVE)

This module integrates thought linking with the dictation flow.
To activate: Set thought_linking.enabled = True in config

Manages the interaction between thought linking decisions and text injection.
"""

import logging
import asyncio
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum

from .thought_linker import ThoughtLinker, LinkingDecision, LinkingSignal

logger = logging.getLogger(__name__)


@dataclass
class InjectionContext:
    """Context for text injection based on linking decision"""

    text: str
    decision: LinkingDecision
    signals: List[LinkingSignal]
    append_space: bool = True
    new_paragraph: bool = False
    clear_buffer: bool = False


class ThoughtLinkingIntegration:
    """
    Integration layer between thought linking and dictation flow - PLACEHOLDER (NOT ACTIVE)

    Manages how text is committed and injected based on thought linking decisions.
    """

    def __init__(self, thought_linker: ThoughtLinker, injection_manager: Any):
        """
        Initialize integration

        Args:
            thought_linker: The thought linking engine
            injection_manager: The injection manager for sending text
        """
        self.thought_linker = thought_linker
        self.injection_manager = injection_manager
        self.enabled = thought_linker.enabled

        # Buffer management
        self._text_buffer = []  # Buffer for accumulating text
        self._last_decision = None

        logger.info(f"ThoughtLinkingIntegration initialized (enabled={self.enabled})")

    async def process_text_with_linking(self, text: str) -> InjectionContext:
        """
        Process text through thought linking and prepare injection context

        Args:
            text: The text to process

        Returns:
            InjectionContext with injection instructions
        """
        # Get linking decision
        decision, signals = self.thought_linker.should_link_thoughts(text)

        # Log decision for debugging
        if self.enabled and signals:
            strongest = max(signals, key=lambda s: s.strength)
            logger.debug(
                f"Linking decision: {decision.value} (strongest signal: {strongest.description})"
            )

        # Create injection context based on decision
        context = self._create_injection_context(text, decision, signals)

        # Update buffer based on decision
        self._update_buffer(text, decision)

        # Store last decision
        self._last_decision = decision

        return context

    def _create_injection_context(
        self, text: str, decision: LinkingDecision, signals: List[LinkingSignal]
    ) -> InjectionContext:
        """Create injection context based on linking decision"""

        # Default context
        context = InjectionContext(text=text, decision=decision, signals=signals)

        if not self.enabled:
            # Simple behavior when disabled
            context.append_space = True
            context.new_paragraph = text.strip().endswith((".", "!", "?"))
            return context

        # Configure based on decision
        if decision == LinkingDecision.APPEND_WITH_SPACE:
            context.append_space = True
            context.new_paragraph = False
            context.clear_buffer = False

        elif decision == LinkingDecision.START_NEW_PARAGRAPH:
            context.append_space = False
            context.new_paragraph = True
            context.clear_buffer = False

        elif decision == LinkingDecision.START_NEW_THOUGHT:
            context.append_space = False
            context.new_paragraph = True
            context.clear_buffer = True

        elif decision == LinkingDecision.COMMIT_AND_CONTINUE:
            context.append_space = True
            context.new_paragraph = False
            context.clear_buffer = False

        return context

    def _update_buffer(self, text: str, decision: LinkingDecision):
        """Update internal text buffer based on decision"""
        if decision == LinkingDecision.START_NEW_THOUGHT:
            # Clear buffer for new thought
            self._text_buffer.clear()
            self._text_buffer.append(text)
        else:
            # Add to existing buffer
            self._text_buffer.append(text)

        # Limit buffer size
        if len(self._text_buffer) > 10:
            self._text_buffer = self._text_buffer[-10:]

    async def inject_with_context(self, context: InjectionContext) -> bool:
        """
        Inject text using the injection manager with proper formatting

        Args:
            context: The injection context

        Returns:
            True if successful, False otherwise
        """
        try:
            # Prepare text for injection
            injection_text = context.text

            # Add formatting based on context
            if context.new_paragraph:
                # Add newline before text for new paragraph
                injection_text = f"\n\n{injection_text}"
            elif context.append_space and self._last_decision:
                # Add space before text if continuing
                injection_text = f" {injection_text}"

            # Inject using the injection manager
            success = await self.injection_manager.inject_text_async(injection_text.strip())

            if success:
                logger.debug(f"Injected text with decision: {context.decision.value}")
            else:
                logger.warning("Text injection failed")

            return success

        except Exception as e:
            logger.error(f"Error during injection: {e}")
            return False

    def register_user_action(self, action: str):
        """
        Register user action with thought linker

        Args:
            action: The user action (e.g., 'enter', 'tab', 'escape')
        """
        self.thought_linker.register_user_action(action)
        logger.debug(f"User action registered: {action}")

    def clear_context(self):
        """Clear all context and buffers"""
        self.thought_linker.clear_context()
        self._text_buffer.clear()
        self._last_decision = None
        logger.debug("Thought linking context cleared")

    def get_buffer_preview(self) -> str:
        """Get preview of current buffer content"""
        if not self._text_buffer:
            return ""

        # Join last few entries
        preview_count = min(3, len(self._text_buffer))
        preview_texts = self._text_buffer[-preview_count:]
        return " ".join(preview_texts)

    def get_debug_info(self) -> Dict[str, Any]:
        """Get debug information"""
        info = self.thought_linker.get_debug_info()
        info.update(
            {
                "buffer_size": len(self._text_buffer),
                "last_decision": self._last_decision.value if self._last_decision else None,
                "buffer_preview": self.get_buffer_preview(),
            }
        )
        return info


def create_thought_linking_integration(
    thought_linker: ThoughtLinker, injection_manager: Any
) -> ThoughtLinkingIntegration:
    """Factory function to create thought linking integration"""
    return ThoughtLinkingIntegration(thought_linker, injection_manager)
