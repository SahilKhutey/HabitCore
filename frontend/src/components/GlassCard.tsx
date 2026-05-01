import React from 'react';
import { View, StyleSheet, ViewProps } from 'react-native';
import { COLORS, SPACING } from '../theme/theme';

interface GlassCardProps extends ViewProps {
  children: React.ReactNode;
  variant?: 'default' | 'highlighted';
}

export function GlassCard({ children, variant = 'default', style, ...props }: GlassCardProps) {
  return (
    <View
      style={[
        styles.card,
        variant === 'highlighted' && styles.highlighted,
        style
      ]}
      {...props}
    >
      {children}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: COLORS.card,
    borderRadius: 20,
    padding: SPACING.md,
    borderWidth: 1,
    borderColor: COLORS.border,
    overflow: 'hidden',
  },
  highlighted: {
    borderColor: COLORS.primary,
    backgroundColor: 'rgba(0, 255, 204, 0.1)',
  }
});
