export const COLORS = {
  // Core palette
  bg: "#0B0F1A",
  card: "rgba(255, 255, 255, 0.05)",
  primary: "#00FFCC",
  secondary: "#8B5CF6",
  accent: "#F59E0B",
  text: "#E5E7EB",
  textSecondary: "#9CA3AF",
  danger: "#EF4444",
  success: "#10B981",
  
  // Gradients
  primaryGradient: ["#00FFCC", "#8B5CF6"],
  
  // UI States
  border: "rgba(255, 255, 255, 0.1)",
  glassBorder: "rgba(255, 255, 255, 0.2)",
};

export const SPACING = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
};

export const TYPOGRAPHY = {
  h1: {
    fontSize: 32,
    fontWeight: '800' as const,
    color: COLORS.text,
    letterSpacing: -0.5,
  },
  h2: {
    fontSize: 24,
    fontWeight: '700' as const,
    color: COLORS.text,
  },
  body: {
    fontSize: 16,
    fontWeight: '400' as const,
    color: COLORS.text,
  },
  caption: {
    fontSize: 14,
    fontWeight: '500' as const,
    color: COLORS.textSecondary,
  },
};
