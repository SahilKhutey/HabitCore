import { create } from 'zustand';

export interface UserState {
  id: string | null;
  email: string | null;
  token: string | null;
  xp: number;
  level: number;
  isPremium: boolean;
  paywallVariant: string;
  mode: string;
  progressStyle: string;
  engagementLevel: string;
  identityGoal: string;
  adaptiveMode: string;
  focusMode: boolean;
  coins: number;
  streakFreeze: number;
  identityPulse: number;
  burnoutScore: number;
  recoveryMode: string;
  setUserInfo: (info: Partial<UserState>) => void;
  updatePreferences: (prefs: Partial<UserState>) => void;
  setToken: (token: string | null) => void;
  addXp: (amount: number) => void;
  resetUser: () => void;
}

export const useUserStore = create<UserState>((set) => ({
  id: null,
  email: null,
  token: null,
  xp: 0,
  level: 1,
  isPremium: false,
  paywallVariant: 'A',
  mode: 'Consistency',
  progressStyle: 'bar',
  engagementLevel: 'Balanced',
  identityGoal: 'Productive',
  adaptiveMode: 'normal',
  focusMode: false,
  coins: 100,
  streakFreeze: 1,
  identityPulse: 0,
  burnoutScore: 0,
  recoveryMode: 'normal',
  setUserInfo: (info) => set((state) => ({ ...state, ...info })),
  updatePreferences: (prefs) => set((state) => ({ ...state, ...prefs })),
  setToken: (token) => set({ token }),
  addXp: (amount) => set((state) => ({ xp: state.xp + amount })),
  resetUser: () => set({ 
    id: null, email: null, token: null, xp: 0, level: 1, isPremium: false, 
    coins: 100, streakFreeze: 1, progressStyle: 'bar', 
    engagementLevel: 'Balanced', identityGoal: 'Productive'
  }),
}));
