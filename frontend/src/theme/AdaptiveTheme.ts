export const ADAPTIVE_THEMES: Record<string, any> = {
  Fit: {
    primary: "#22c55e",
    background: "#001a10",
    accent: "#4ade80"
  },
  Learner: {
    primary: "#3b82f6",
    background: "#080c14",
    accent: "#60a5fa"
  },
  Productive: {
    primary: "#a855f7",
    background: "#0f0814",
    accent: "#c084fc"
  },
  Calm: {
    primary: "#06b6d4",
    background: "#081014",
    accent: "#22d3ee"
  },
  default: {
    primary: "#00ffcc",
    background: "#000000",
    accent: "#f59e0b"
  }
};

export const getTheme = (identity: string) => {
  return ADAPTIVE_THEMES[identity] || ADAPTIVE_THEMES.default;
};
