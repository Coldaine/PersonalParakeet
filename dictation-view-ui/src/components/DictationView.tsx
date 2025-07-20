import { motion, AnimatePresence } from "framer-motion";
import { useTranscriptionStore, toggleClarity, commitText, clearText } from "../stores/transcriptionStore";
import { useEffect, useState } from "react";
import { invoke } from "@tauri-apps/api/tauri";
import clsx from "clsx";
import "./DictationView.css";

interface DictationViewProps {
  isVisible: boolean;
}

interface VADStatus {
  isActive: boolean;
  audioLevel: number;
  pauseDuration: number;
  willCommitIn: number; // ms until auto-commit
}

export function DictationView({ isVisible }: DictationViewProps) {
  const { 
    text, 
    correctedText, 
    mode, 
    confidence, 
    isListening, 
    isConnected, 
    clarityEnabled, 
    correctionInfo, 
    lastUpdateType 
  } = useTranscriptionStore();
  const [showCursor, setShowCursor] = useState(true);
  const [vadStatus, setVadStatus] = useState<VADStatus>({
    isActive: false,
    audioLevel: 0,
    pauseDuration: 0,
    willCommitIn: 0
  });

  useEffect(() => {
    // Blink cursor
    const interval = setInterval(() => {
      setShowCursor(prev => !prev);
    }, 500);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    // Update window size based on mode
    const updateWindowSize = async () => {
      const sizes = {
        compact: { width: 400, height: 80 },
        standard: { width: 600, height: 150 },
        extended: { width: 800, height: 300 }
      };
      
      const { width, height } = sizes[mode];
      await invoke("update_size", { width, height });
    };

    if (isVisible) {
      updateWindowSize();
    }
  }, [mode, isVisible]);

  // WebSocket message handling
  useEffect(() => {
    const ws = useTranscriptionStore.getState().ws;
    if (ws) {
        ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            if (message.type === 'vad_status') {
                setVadStatus(message.data);
            }
            useTranscriptionStore.getState().handleMessage(message);
        };
    }
  }, []);

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          className={clsx("dictation-view", mode, {
            "listening": isListening,
            "clarity-enabled": clarityEnabled,
            "corrected": lastUpdateType === 'corrected',
            "raw": lastUpdateType === 'raw',
            "high-confidence": confidence > 0.9,
            "medium-confidence": confidence > 0.7 && confidence <= 0.9,
            "low-confidence": confidence <= 0.7
          })}
          initial={{ opacity: 0, scale: 0.9, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.9, y: 20 }}
          transition={{ 
            duration: 0.2,
            ease: [0.4, 0, 0.2, 1]
          }}
          data-tauri-drag-region
          style={{ cursor: "move" }}
        >
          {/* Status indicator */}
          <div className="status-indicator">
            <motion.div 
              className={`status-dot ${!isConnected ? 'disconnected' : ''}`}
              animate={isConnected && isListening ? {
                scale: [1, 1.2, 1],
                opacity: [0.8, 1, 0.8]
              } : {}}
              transition={{
                duration: 1.5,
                repeat: Infinity,
                ease: "easeInOut"
              }}
              title={!isConnected ? "Disconnected from backend" : isListening ? "Listening..." : "Connected"}
            />
          </div>

          {/* VAD Status Indicator */}
          <div className="vad-indicator">
            <div className={clsx("microphone-icon", { active: vadStatus.isActive })} />
            <div className="audio-level-bar">
              <div 
                className="level-fill"
                style={{ width: `${vadStatus.audioLevel * 100}%` }}
              />
            </div>
          </div>

          {/* Auto-commit countdown */}
          {vadStatus.willCommitIn > 0 && (
            <div className="commit-countdown">
              Auto-commit in {Math.ceil(vadStatus.willCommitIn / 1000)}s
            </div>
          )}

          {/* Clarity Engine Controls */}
          <div className="clarity-controls">
            <button 
              className={`clarity-toggle ${clarityEnabled ? 'enabled' : 'disabled'}`}
              onClick={toggleClarity}
              title={`Clarity Engine: ${clarityEnabled ? 'ON' : 'OFF'}`}
            >
              ✨
            </button>
            <button 
              className="commit-btn"
              onClick={commitText}
              title="Commit text (Ctrl+Enter)"
            >
              ✓
            </button>
            <button 
              className="clear-btn"
              onClick={clearText}
              title="Clear text (Escape)"
            >
              ✗
            </button>
          </div>

          {/* Main content */}
          <div className="content">
            <motion.div 
              className="text-content"
              animate={{ opacity: 1 }}
              transition={{ duration: 0.3 }}
            >
              {/* Show corrected text if available, otherwise raw text */}
              <div className="primary-text">
                {correctedText || text}
                {showCursor && <span className="cursor">|</span>}
              </div>
              
              {/* Show original text if corrections were made */}
              {correctedText && correctedText !== text && (
                <div className="original-text">
                  <span className="label">Original:</span> {text}
                </div>
              )}
              
              {/* Show correction info */}
              {correctionInfo && correctionInfo.corrections.length > 0 && (
                <div className="correction-info">
                  <span className="correction-count">
                    {correctionInfo.corrections.length} correction{correctionInfo.corrections.length !== 1 ? 's' : ''}
                  </span>
                  <span className="processing-time">
                    {correctionInfo.processingTimeMs.toFixed(0)}ms
                  </span>
                </div>
              )}
            </motion.div>

            {/* Confidence indicator */}
            {confidence > 0 && (
              <div className="confidence-bar">
                <motion.div 
                  className="confidence-fill"
                  initial={{ width: 0 }}
                  animate={{ width: `${confidence * 100}%` }}
                  transition={{ duration: 0.3 }}
                />
              </div>
            )}
          </div>

          {/* Thought linking indicator */}
          {mode === "standard" || mode === "extended" && (
            <div className="linking-indicator">
              <span className="linking-dot" />
              <span className="linking-dot" />
              <span className="linking-dot" />
            </div>
          )}

          {/* Particles for thinking effect */}
          <div className="particles">
            {[...Array(5)].map((_, i) => (
              <motion.div
                key={i}
                className="particle"
                initial={{ opacity: 0, y: 0 }}
                animate={{
                  opacity: [0, 1, 0],
                  y: -30,
                  x: Math.random() * 40 - 20
                }}
                transition={{
                  duration: 2,
                  delay: i * 0.2,
                  repeat: Infinity,
                  ease: "easeOut"
                }}
              />
            ))}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}