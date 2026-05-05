import { create } from 'zustand';

interface Nudge {
  id: string;
  message: string;
  type: 'action' | 'reminder' | 'success' | 'error';
  actionLabel?: string;
  onAction?: () => void;
}

interface NudgeStore {
  activeNudge: Nudge | null;
  showNudge: (nudge: Omit<Nudge, 'id'>) => void;
  hideNudge: () => void;
}

export const useNudgeStore = create<NudgeStore>((set) => ({
  activeNudge: null,
  showNudge: (nudge) => set({ 
    activeNudge: { ...nudge, id: Math.random().toString(36).substr(2, 9) } 
  }),
  hideNudge: () => set({ activeNudge: null }),
}));

export const NudgeService = {
  show: (message: string, type: Nudge['type'] = 'reminder', actionLabel?: string, onAction?: () => void) => {
    useNudgeStore.getState().showNudge({ message, type, actionLabel, onAction });
  },
  success: (message: string) => {
    useNudgeStore.getState().showNudge({ message, type: 'success' });
  },
  error: (message: string) => {
    useNudgeStore.getState().showNudge({ message, type: 'error' });
  },
  hide: () => {
    useNudgeStore.getState().hideNudge();
  }
};
