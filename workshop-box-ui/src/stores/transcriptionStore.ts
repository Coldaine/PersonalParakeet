import { create } from 'zustand';

interface TranscriptionState {
  text: string;
  mode: 'compact' | 'standard' | 'extended';
  confidence: number;
  isListening: boolean;
  isConnected: boolean;
  commandMode: boolean;
  
  // Actions
  setText: (text: string) => void;
  setMode: (mode: 'compact' | 'standard' | 'extended') => void;
  setConfidence: (confidence: number) => void;
  setListening: (listening: boolean) => void;
  setConnected: (connected: boolean) => void;
  setCommandMode: (commandMode: boolean) => void;
  clear: () => void;
}

export const useTranscriptionStore = create<TranscriptionState>((set) => ({
  text: '',
  mode: 'compact',
  confidence: 0,
  isListening: false,
  isConnected: false,
  commandMode: false,
  
  setText: (text) => {
    set({ text });
    
    // Auto-detect mode based on word count
    const wordCount = text.split(' ').length;
    if (wordCount <= 10) {
      set({ mode: 'compact' });
    } else if (wordCount <= 50) {
      set({ mode: 'standard' });
    } else {
      set({ mode: 'extended' });
    }
  },
  
  setMode: (mode) => set({ mode }),
  setConfidence: (confidence) => set({ confidence }),
  setListening: (listening) => set({ isListening: listening }),
  setConnected: (connected) => set({ isConnected: connected }),
  setCommandMode: (commandMode) => set({ commandMode }),
  
  clear: () => set({
    text: '',
    mode: 'compact',
    confidence: 0,
    isListening: false,
    isConnected: false,
    commandMode: false
  })
}));