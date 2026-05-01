import { create } from 'zustand';

export interface UserState {
  id: string | null;
  email: string | null;
  token: string | null;
   xp: number;
   currentXP: number;
   nextLevelXP: number;
   level: number;
   isPremium: boolean;
   paywall_variant: string;
   mode: string;
    progress_style: string;
    engagement_level: string;
    identity_goal: string;
   adaptiveMode: string;
   focusMode: boolean;
   coins: number;
   streakFreeze: number;
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
  currentXP: 0,
  nextLevelXP: 100,
  level: 1,
  isPremium: false,
  paywall_variant: 'A',
  mode: 'Consistency',
  progress_style: 'bar',
  engagement_level: 'Balanced',
  identity_goal: 'Productive',
  adaptiveMode: 'normal',
  focusMode: false,
  coins: 100,
  streakFreeze: 1,
  setUserInfo: (info) => set((state) => ({ ...state, ...info })),
  updatePreferences: (prefs) => set((state) => ({ ...state, ...prefs })),
  setToken: (token) => set({ token }),
  addXp: (amount) => set((state) => ({ xp: state.xp + amount })),
  resetUser: () => set({ 
    id: null, email: null, token: null, xp: 0, currentXP: 0, nextLevelXP: 100, 
    level: 1, isPremium: false, coins: 100, streakFreeze: 1,
    progress_style: 'bar', engagement_level: 'Balanced', identity_goal: 'Productive'
  }),
}));
