export const COLORS = {
  background: '#0D0D0D',
  surface: '#1A1A1A',
  surfaceLight: '#2A2A2A',
  primary: '#8B5CF6', // Purple
  secondary: '#10B981', // Green
  accent: '#F59E0B', // Amber
  neonGreen: '#00FFCC',
  neonPurple: '#BF40BF',
  gold: '#FFD700',
  text: '#FFFFFF',
  textSecondary: '#A1A1AA',
  error: '#EF4444',
  glass: 'rgba(255, 255, 255, 0.05)',
  glassBorder: 'rgba(255, 255, 255, 0.1)',
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
    fontWeight: '700' as const,
    color: COLORS.text,
  },
  h2: {
    fontSize: 24,
    fontWeight: '600' as const,
    color: COLORS.text,
  },
  body: {
    fontSize: 16,
    color: COLORS.text,
  },
  caption: {
    fontSize: 12,
    color: COLORS.textSecondary,
  },
};
