import { create } from 'zustand';

export interface UserState {
  id: string | null;
  email: string | null;
  token: string | null;
  xp: number;
  level: number;
  isPremium: boolean;
  paywall_variant: string;
  mode: string;
  style: string;
  engagement: string;
  identity: string;
  adaptiveMode: string;
  focusMode: boolean;
  coins: number;
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
  paywall_variant: 'A',
  mode: 'Consistency',
  style: 'bar',
  engagement: 'Balanced',
  identity: 'Productive',
  adaptiveMode: 'normal',
  focusMode: false,
  coins: 100,
  setUserInfo: (info) => set((state) => ({ ...state, ...info })),
  updatePreferences: (prefs) => set((state) => ({ ...state, ...prefs })),
  setToken: (token) => set({ token }),
  addXp: (amount) => set((state) => {
    const newXp = state.xp + amount;
    const newLevel = Math.floor(newXp / 100) + 1;
    return { xp: newXp, level: newLevel };
  }),
  resetUser: () => set({ id: null, email: null, token: null, xp: 0, level: 1, isPremium: false, coins: 100 }),
}));
