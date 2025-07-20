import { useEffect, useState } from "react";
import { listen } from "@tauri-apps/api/event";
import { appWindow } from "@tauri-apps/api/window";
import { DictationView } from "./components/DictationView";
import { useTranscriptionStore } from "./stores/transcriptionStore";
import "./App.css";

interface TranscriptionPayload {
  text: string;
  mode: string;
  confidence: number;
}

function App() {
  const { setText, setMode, setConfidence, setConnected } = useTranscriptionStore();
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    // Listen for transcription events from Rust backend
    const unlisten = listen<TranscriptionPayload>("transcription", (event) => {
      const { text, mode, confidence } = event.payload;
      setText(text);
      setMode(mode as "compact" | "standard" | "extended");
      setConfidence(confidence);
      setIsVisible(true);
      setConnected(true);
    });
    
    // Listen for connection status
    const unlistenStatus = listen<{is_listening: boolean}>("status", (event) => {
      setConnected(event.payload.is_listening);
    });

    // Set up keyboard shortcuts
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setIsVisible(false);
        setText("");
      }
    };

    window.addEventListener("keydown", handleKeyPress);

    return () => {
      unlisten.then(fn => fn());
      unlistenStatus.then(fn => fn());
      window.removeEventListener("keydown", handleKeyPress);
    };
  }, [setText, setMode, setConfidence]);

  return (
    <div className="app-container">
      <DictationView isVisible={isVisible} />
    </div>
  );
}

export default App;