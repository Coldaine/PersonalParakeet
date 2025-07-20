import { motion, AnimatePresence } from "framer-motion";
import { useTranscriptionStore } from "../stores/transcriptionStore";
import { useEffect, useState } from "react";
import { invoke } from "@tauri-apps/api/tauri";
import clsx from "clsx";
import "./WorkshopBox.css";

interface WorkshopBoxProps {
  isVisible: boolean;
}

export function WorkshopBox({ isVisible }: WorkshopBoxProps) {
  const { text, mode, confidence, isListening, isConnected } = useTranscriptionStore();
  const [showCursor, setShowCursor] = useState(true);

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

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          className={clsx("workshop-box", mode, {
            "listening": isListening,
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

          {/* Main content */}
          <div className="content">
            <motion.div 
              className="text-content"
              animate={{ opacity: 1 }}
              transition={{ duration: 0.3 }}
            >
              {text}
              {showCursor && <span className="cursor">|</span>}
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