export interface Streak {
  current_streak: number;
  longest_streak: number;
  last_completion: string | null;
}

export interface Habit {
  id: string;
  name: string;
  title?: string;
  done: boolean;
  difficulty: 'easy' | 'medium' | 'hard';
  streak?: Streak;
  created_at: string;
}

export interface User {
  id: string;
  email: string;
  xp: number;
  level: number;
  is_premium: boolean;
  coins: number;
  identity_goal: string;
}

export interface LeaderboardUser {
  id: string;
  name: string;
  score: number;
  is_me: boolean;
  is_premium?: boolean;
}
