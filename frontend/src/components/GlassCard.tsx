import React from 'react';
import { View, StyleSheet, ViewProps, Platform } from 'react-native';
import { BlurView } from 'expo-blur';
import { COLORS, SPACING } from '../theme/theme';

interface GlassCardProps extends ViewProps {
  children: React.ReactNode;
  variant?: 'default' | 'highlighted' | 'ai';
}

export function GlassCard({ children, variant = 'default', style, ...props }: GlassCardProps) {
  return (
    <View style={[styles.container, style]} {...props}>
      {Platform.OS !== 'web' ? (
        <BlurView intensity={20} tint="dark" style={StyleSheet.absoluteFill} />
      ) : (
        <View style={[StyleSheet.absoluteFill, { backgroundColor: COLORS.glassBg, backdropFilter: 'blur(20px)' } as any]} />
      )}
      <View
        style={[
          styles.card,
          variant === 'highlighted' && styles.highlighted,
          variant === 'ai' && styles.ai,
        ]}
      >
        {children}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    borderRadius: 20,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
  },
  card: {
    padding: SPACING.lg,
    backgroundColor: 'transparent',
  },
  highlighted: {
    borderWidth: 1.5,
    borderColor: COLORS.primary,
  },
  ai: {
    borderWidth: 1.5,
    borderColor: COLORS.secondary,
    shadowColor: COLORS.secondary,
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.2,
    shadowRadius: 10,
  }
});
