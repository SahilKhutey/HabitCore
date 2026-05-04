/**
 * HabitCore Design System
 * Production-ready tokens for React Native
 * Calm, Intelligent, Introspective
 */

export const COLORS = {
  // Base Colors
  background: "#0F1115",
  surface: "#151821",
  surfaceLight: "#1C1F2A",
  
  text: "#FFFFFF",
  textSecondary: "#AAB0C0",
  textDim: "#6B7280",
  
  border: "#2A2F3A",
  
  // Accent System
  primary: "#7C8CFF",
  primaryGlow: "rgba(124, 140, 255, 0.25)",
  
  success: "#4ADE80",
  warning: "#FBBF24",
  danger: "#F87171",
  
  // Identity Pulse
  identity: {
    discipline: "#7C8CFF",
    awareness: "#A78BFA",
    avoidance: "#F87171",
  }
};

export const SPACING = {
  0: 0,
  1: 4,
  2: 8,
  3: 12,
  4: 16,
  5: 20,
  6: 24,
  8: 32,
  10: 40,
  12: 48,
  
  // Semantic mapping
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  gutter: 16,
  margin: 20,
};

export const RADIUS = {
  sm: 6,
  md: 10,
  lg: 16,
  xl: 24,
  full: 999,
};

export const SHADOWS = {
  card: {
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.25,
    shadowRadius: 20,
    elevation: 5,
  },
  glowPrimary: {
    shadowColor: "#7C8CFF",
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.35,
    shadowRadius: 20,
    elevation: 10,
  }
};

export const TYPOGRAPHY = {
  family: "Inter, system-ui", // Fallback to system fonts in RN
  size: {
    xs: 12,
    sm: 14,
    md: 16,
    lg: 20,
    xl: 24,
    xxl: 32,
  },
  weight: {
    regular: "400" as const,
    medium: "500" as const,
    semibold: "600" as const,
    bold: "700" as const,
  },
  
  // Presets
  h1: {
    fontFamily: "SpaceGrotesk_700Bold", // Keeping SpaceGrotesk for headers for character
    fontSize: 32,
    fontWeight: "700" as const,
    color: COLORS.text,
  },
  h2: {
    fontFamily: "SpaceGrotesk_600SemiBold",
    fontSize: 24,
    fontWeight: "600" as const,
    color: COLORS.text,
  },
  h3: {
    fontFamily: "Inter_600SemiBold",
    fontSize: 18,
    fontWeight: "600" as const,
    color: COLORS.text,
  },
  body: {
    fontFamily: "Inter_400Regular",
    fontSize: 16,
    color: COLORS.textSecondary,
    lineHeight: 24,
  },
  bodyLg: {
    fontFamily: "Inter_400Regular",
    fontSize: 20,
    color: COLORS.text,
    lineHeight: 30,
  },
  label: {
    fontFamily: "Inter_500Medium",
    fontSize: 14,
    fontWeight: "500" as const,
    letterSpacing: 1,
    textTransform: "uppercase" as const,
  },
  caption: {
    fontFamily: "Inter_400Regular",
    fontSize: 12,
    color: COLORS.textDim,
  }
};
