# Architectural Brief: PersonalParakeet v2.0

**To:** The PersonalParakeet Implementation Agent/Team  
**From:** Project Architect  
**Date:** July 19, 2025  
**Subject:** Definitive Implementation Strategy for the "Workshop" Model

## 1. Executive Summary: A Shift in Philosophy

This document outlines the revised and final architectural direction for the PersonalParakeet dictation system. The project's core mission remains the same: to deliver a fluid, "thought-to-text" experience that is superior to existing solutions. However, we are pivoting away from a model that relies on complex, invisible backend algorithms for text stabilization.

The new architecture, **"The Workshop Model,"** achieves our goals through a more elegant, transparent, and user-centric UI/UX design. This approach dramatically simplifies the backend logic, reduces potential points of failure, and gives the user a greater sense of control and transparency. Our primary innovation is no longer a complex buffering algorithm, but rather a clever user interface that contains the "messiness" of real-time AI transcription, delivering a perfectly clean result to the user's target application.

## 2. Core Component: The "Workshop" UI

The centerpiece of this architecture is the **"Workshop Box,"** a semi-transparent, borderless, always-on-top UI element.

- **Behavior:** The Workshop Box appears near the user's cursor or in a fixed screen position the moment speech is detected. It serves as a "scratchpad" for the live transcription process.

- **Real-Time Feedback:** Inside this box, the user will see the raw, real-time output from the Speech-to-Text (STT) engine. This includes the "flickering" and "rewriting" of words as the AI model gains more context. This is a deliberate design choice: we are exposing the process to the user in a contained, non-disruptive way.

- **Engine:** The text displayed in this box is powered by the "Clarity Engine," a fast, local LLM that performs real-time contextual correction (fixing homophones, jargon, etc.). The user sees these corrections happen live within the box.

- **Implementation Priority:** The development of a performant, visually appealing, and reliable cross-platform (Windows, Linux) Workshop Box is the highest technical priority. The success of the entire user experience hinges on this component.

## 3. Core Component: The "Commit & Control" Logic

The user has explicit control over how the finalized text from the Workshop Box is handled. The system must implement three distinct "commit actions":

| Action | User Trigger(s) | System Actions |
|--------|----------------|----------------|
| **Commit & Continue** | A sustained pause in speech (configurable, e.g., >1.5 seconds). | 1. Finalize the text in the Workshop Box.<br>2. Inject the text into the target application.<br>3. Leave the cursor at the end of the injected text.<br>4. Hide the Workshop Box. |
| **Commit & Execute** | Pressing the Enter key while speaking, or using a specific voice command (see Section 4). | 1. Finalize the text in the Workshop Box.<br>2. Inject the text into the target application.<br>3. Simulate an Enter key press.<br>4. Hide the Workshop Box. |
| **Abort & Clear** | Pressing the Escape key while speaking, or using a specific voice command. | 1. Immediately discard all text in the Workshop Box.<br>2. Hide the Workshop Box.<br>3. Do not inject any text. |

## 4. Core Component: The "Command Mode" Pattern

To ensure commands are executed with perfect accuracy and to eliminate false positives, we will implement a strict, two-step command pattern.

- **Activation Phrase:** The user must first say a unique, acoustically distinct "magic phrase" that is highly unlikely to be spoken in normal dictation. The default phrase will be **"Parakeet Command."** This phrase must be easily user-configurable.

- **Command Listening State:** Upon detecting this phrase with high confidence, the system enters a temporary "Command Listening" mode. The UI must provide clear feedback that this mode is active (e.g., the border of the Workshop Box briefly flashes blue).

- **Command Execution:** The next utterance from the user is interpreted as a command (e.g., "run that," "cancel," "delete last sentence"). The system executes the corresponding action and immediately returns to normal dictation mode.

This design prioritizes reliability and user trust over conversational fluidity for commands.

## 5. Core Component: "Intelligent Thought-Linking"

A simple pause-based commit is not sufficient for all use cases. The system must be able to intelligently link consecutive utterances into a single, coherent thought. This logic is triggered after a pause is detected but before the "Commit & Continue" action is executed.

The system will check a hierarchy of contextual signals to decide whether to append the new text to the previous thought (with a leading space) or to treat it as a new paragraph (simulating an Enter key press before injection).

### Primary Signals (High Priority):
- Has the user manually pressed Enter, Tab, or Escape? (If yes, always start a new thought).
- Has the active application window changed? (If yes, start a new thought).
- Has the cursor's position moved significantly? (If yes, start a new thought).

### Secondary Signal (Lower Priority):
- If none of the primary signals are present, perform a quick semantic similarity check between the newly finalized text and the previously injected text. If they are highly related, append them. Otherwise, start a new thought.

This agent's role is to provide a layer of intelligent formatting, making the final output more natural and reducing the need for manual edits.

## 6. High-Level Data Flow (Typical Interaction)

1. User begins speaking.
2. The Workshop Box UI appears.
3. Audio is streamed to the local STT engine.
4. The raw transcription is passed to the Clarity Engine (LLM) for real-time correction.
5. The corrected, yet still "flickering," text is displayed in the Workshop Box.
6. User pauses for 1.5 seconds, triggering the Commit & Continue logic.
7. The Intelligent Thought-Linking agent runs its checks and determines this is a continuation of the previous sentence.
8. The finalized text is injected into the target application with a leading space.
9. The Workshop Box disappears. The system is ready for the next utterance.

---

This architecture represents a mature, robust, and user-centric vision for PersonalParakeet. The implementation should prioritize the creation of a seamless and performant UI, as it is now the central pillar of the entire user experience.