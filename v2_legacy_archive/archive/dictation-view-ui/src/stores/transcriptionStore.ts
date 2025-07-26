import { create } from 'zustand';

export interface CorrectionInfo {
  original: string;
  corrected: string;
  corrections: Array<[string, string]>;
  processingTimeMs: number;
  confidence: number;
}

export interface VADStatus {
  isActive: boolean;
  audioLevel: number;
  pauseDuration: number;
  willCommitIn: number; // ms until auto-commit
}

interface TranscriptionState {
  text: string;
  correctedText?: string;
  mode: 'compact' | 'standard' | 'extended';
  confidence: number;
  isListening: boolean;
  isConnected: boolean;
  commandMode: boolean;
  clarityEnabled: boolean;
  commandModeEnabled: boolean;
  commandStatus?: {
    lastCommand: string;
    status: 'recognized' | 'executed' | 'failed';
    result: string;
  };
  correctionInfo?: CorrectionInfo;
  lastUpdateType: 'raw' | 'corrected' | 'command' | 'none';
  vadStatus: VADStatus;
  ws: WebSocket | null;

  // Actions
  setText: (text: string) => void;
  setCorrectedText: (text: string, correctionInfo?: CorrectionInfo) => void;
  setMode: (mode: 'compact' | 'standard' | 'extended') => void;
  setConfidence: (confidence: number) => void;
  setListening: (listening: boolean) => void;
  setConnected: (connected: boolean) => void;
  setCommandMode: (commandMode: boolean) => void;
  setClarityEnabled: (enabled: boolean) => void;
  setCommandModeEnabled: (enabled: boolean) => void;
  setCommandStatus: (status: { lastCommand: string; status: 'recognized' | 'executed' | 'failed'; result: string; }) => void;
  setVadStatus: (status: VADStatus) => void;
  handleMessage: (message: any) => void;
  connectWebSocket: () => void;
  clear: () => void;
}

export const useTranscriptionStore = create<TranscriptionState>((set, get) => ({
  text: '',
  correctedText: undefined,
  mode: 'compact',
  confidence: 0,
  isListening: false,
  isConnected: false,
  commandMode: false,
  clarityEnabled: true,
  commandModeEnabled: true,
  commandStatus: undefined,
  correctionInfo: undefined,
  lastUpdateType: 'none',
  vadStatus: { isActive: false, audioLevel: 0, pauseDuration: 0, willCommitIn: 0 },
  ws: null,
  
  setText: (text) => {
    set({ text, lastUpdateType: 'raw' });
    
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
  
  setCorrectedText: (correctedText, correctionInfo) => {
    set({ 
      correctedText, 
      correctionInfo, 
      lastUpdateType: 'corrected' 
    });
  },
  
  setMode: (mode) => set({ mode }),
  setConfidence: (confidence) => set({ confidence }),
  setListening: (listening) => set({ isListening: listening }),
  setConnected: (connected) => set({ isConnected: connected }),
  setCommandMode: (commandMode) => set({ commandMode }),
  setClarityEnabled: (enabled) => set({ clarityEnabled: enabled }),
  setCommandModeEnabled: (enabled) => set({ commandModeEnabled: enabled }),
  setCommandStatus: (status) => set({ commandStatus: status, lastUpdateType: 'command' }),
  setVadStatus: (status) => set({ vadStatus: status }),

  handleMessage: (data) => {
      const store = get();
      
      if (data.type === 'raw_transcription') {
        // Raw STT output - show immediately
        store.setText(data.text);
        
      } else if (data.type === 'corrected_transcription') {
        // Clarity Engine corrected text
        const correctionInfo: CorrectionInfo = {
          original: data.text,
          corrected: data.corrected_text || data.text,
          corrections: data.corrections_made || [],
          processingTimeMs: data.correction_time_ms || 0,
          confidence: data.confidence || 0.8
        };
        
        store.setCorrectedText(data.corrected_text || data.text, correctionInfo);
        
      } else if (data.type === 'dictation_status') {
        store.setListening(data.is_listening);
        if (data.clarity_enabled !== undefined) {
          store.setClarityEnabled(data.clarity_enabled);
        }
        
      } else if (data.type === 'clarity_status') {
        store.setClarityEnabled(data.enabled);
        
      } else if (data.type === 'command_mode_status') {
        store.setCommandModeEnabled(data.enabled);
        
      } else if (data.type === 'command') {
        // Handle command feedback
        store.setCommandStatus({
          lastCommand: data.command,
          status: data.status,
          result: data.result || ''
        });
        
      } else if (data.type === 'commit_text' || data.type === 'clear_text') {
        // Text was committed or cleared - clear the workshop box
        store.clear();
        
      } else if (data.type === 'transcription') {
        // Legacy support
        store.setText(data.text);
      } else if (data.type === 'vad_status') {
        store.setVadStatus(data.data);
      }
  },

  connectWebSocket: () => {
    try {
      const ws = new WebSocket('ws://127.0.0.1:8765');
      set({ ws });
      
      ws.onopen = () => {
        console.log('Connected to WebSocket');
        get().setConnected(true);
      };
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('Received:', data);
        get().handleMessage(data);
      };
      
      ws.onclose = () => {
        console.log('WebSocket connection closed');
        get().setConnected(false);
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        get().setConnected(false);
      };
    } catch (error) {
      console.error('Failed to connect to WebSocket:', error);
    }
  },
  
  clear: () => set({
    text: '',
    correctedText: undefined,
    mode: 'compact',
    confidence: 0,
    correctionInfo: undefined,
    lastUpdateType: 'none'
  })
}));

export function sendCommand(command: string, data?: any) {
  const ws = useTranscriptionStore.getState().ws;
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ command, ...data }));
  }
}

export function toggleClarity() {
  sendCommand('toggle_clarity');
}

export function commitText() {
  sendCommand('commit_text');
}

export function clearText() {
  sendCommand('clear_text');
}

export function toggleCommandMode() {
  sendCommand('toggle_command_mode');
}
