export const COLORS = {
  // Core palette
  background: "#0f172a", // Lighter slate blue
  surface: "#0f172a",
  surfaceLight: "#1e293b",
  primary: "#33ffd6", // Softer neon teal
  secondary: "#a78bfa", // Softer lavender
  accent: "#fbbf24",
  text: "#f8fafc",
  textSecondary: "#94a3b8",
  textDim: "#64748b",
  danger: "#f87171",
  success: "#33ffd6",
  gold: "#fbbf24",
  
  // Gradients
  primaryGradient: ["#33ffd6", "#38bdf8"],
  secondaryGradient: ["#a78bfa", "#e879f9"],
  surfaceGradient: ["rgba(30, 41, 59, 0.5)", "rgba(15, 23, 42, 0.3)"],
  
  // UI States
  border: "rgba(255, 255, 255, 0.08)",
  glassBorder: "rgba(255, 255, 255, 0.15)",
  glassBg: "rgba(30, 41, 59, 0.4)",
};

export const SPACING = {
  unit: 4,
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 48,
  gutter: 16,
  margin: 24,
};

export const TYPOGRAPHY = {
  h1: {
    fontFamily: 'SpaceGrotesk_700Bold',
    fontSize: 32,
    color: COLORS.text,
    letterSpacing: -0.5,
  },
  h2: {
    fontFamily: 'SpaceGrotesk_600SemiBold',
    fontSize: 24,
    color: COLORS.text,
  },
  h3: {
    fontFamily: 'SpaceGrotesk_600SemiBold',
    fontSize: 20,
    color: COLORS.text,
  },
  body: {
    fontFamily: 'Inter_400Regular',
    fontSize: 16,
    color: COLORS.text,
  },
  bodyLg: {
    fontFamily: 'Inter_400Regular',
    fontSize: 18,
    color: COLORS.text,
  },
  label: {
    fontFamily: 'SpaceGrotesk_500Medium',
    fontSize: 14,
    color: COLORS.textSecondary,
    letterSpacing: 0.5,
  },
  caption: {
    fontFamily: 'SpaceGrotesk_500Medium',
    fontSize: 12,
    color: COLORS.textDim,
  },
};
