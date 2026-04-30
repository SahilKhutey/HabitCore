import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { COLORS, SPACING, TYPOGRAPHY } from '../theme/theme';

interface XPBarProps {
  xp: number;
  level: number;
}

export const XPBar: React.FC<XPBarProps> = ({ xp, level }) => {
  const progress = xp % 100;

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={TYPOGRAPHY.body}>Level {level}</Text>
        <Text style={TYPOGRAPHY.caption}>{xp % 100} / 100 XP</Text>
      </View>
      <View style={styles.barContainer}>
        <View style={[styles.progress, { width: `${progress}%` }]} />
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: SPACING.md,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
    marginBottom: SPACING.xs,
  },
  barContainer: {
    height: 12,
    backgroundColor: COLORS.surfaceLight,
    borderRadius: 6,
    overflow: 'hidden',
  },
  progress: {
    height: '100%',
    backgroundColor: COLORS.primary,
    borderRadius: 6,
  },
});
