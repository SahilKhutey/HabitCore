import React, { useEffect, useRef } from 'react';
import { View, Text, StyleSheet, Animated } from 'react-native';
import { COLORS, TYPOGRAPHY, SPACING } from '../theme/theme';

interface HabitHeaderProps {
  level: number;
  currentXP: number;
  nextLevelXP: number;
  streak: number;
  coins: number;
  identityGoal?: string;
}

export const HabitHeader: React.FC<HabitHeaderProps> = ({
  level,
  currentXP,
  nextLevelXP,
  streak,
  coins,
  identityGoal = 'Pioneer',
}) => {
  const progress = Math.min(currentXP / Math.max(nextLevelXP, 1), 1);
  const barAnim = useRef(new Animated.Value(0)).current;
  const glowAnim = useRef(new Animated.Value(0.5)).current;

  useEffect(() => {
    Animated.spring(barAnim, {
      toValue: progress,
      tension: 40,
      friction: 8,
      useNativeDriver: false,
    }).start();

    Animated.loop(
      Animated.sequence([
        Animated.timing(glowAnim, { toValue: 1, duration: 1800, useNativeDriver: false }),
        Animated.timing(glowAnim, { toValue: 0.5, duration: 1800, useNativeDriver: false }),
      ])
    ).start();
  }, [progress]);

  const barWidth = barAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ['0%', '100%'],
  });

  const glowOpacity = glowAnim.interpolate({
    inputRange: [0.5, 1],
    outputRange: [0.4, 0.9],
  });

  return (
    <View style={styles.container}>
      {/* Left — Level Badge */}
      <Animated.View style={[styles.levelBadge, { shadowOpacity: glowOpacity as any }]}>
        <Text style={styles.levelNum}>{level}</Text>
        <Text style={styles.levelLabel}>LVL</Text>
      </Animated.View>

      {/* Center — XP Bar + Identity */}
      <View style={styles.centerBlock}>
        <View style={styles.topRow}>
          <Text style={styles.archetypeText}>
            {identityGoal.toUpperCase()} ARCHETYPE
          </Text>
          <Text style={styles.xpText}>
            {currentXP} <Text style={styles.xpDim}>/ {nextLevelXP} XP</Text>
          </Text>
        </View>
        <View style={styles.barTrack}>
          <Animated.View
            style={[styles.barFill, { width: barWidth }]}
          />
          <Animated.View
            style={[styles.barGlow, { width: barWidth, opacity: glowOpacity }]}
          />
        </View>
      </View>

      {/* Right — Streak + Coins */}
      <View style={styles.statsBlock}>
        <View style={styles.statChip}>
          <Text style={styles.statEmoji}>🔥</Text>
          <Text style={styles.statChipText}>{streak}</Text>
        </View>
        <View style={[styles.statChip, { marginTop: 4 }]}>
          <Text style={styles.statEmoji}>💰</Text>
          <Text style={styles.statChipText}>{coins}</Text>
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(30, 41, 59, 0.6)',
    borderRadius: 20,
    borderWidth: 1,
    borderColor: 'rgba(51, 255, 214, 0.15)',
    padding: 14,
    marginBottom: 16,
  },
  levelBadge: {
    width: 52,
    height: 52,
    borderRadius: 16,
    backgroundColor: COLORS.primary,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: COLORS.primary,
    shadowOffset: { width: 0, height: 0 },
    shadowRadius: 12,
    elevation: 8,
    marginRight: 12,
  },
  levelNum: {
    fontFamily: 'SpaceGrotesk_700Bold',
    fontSize: 20,
    color: '#0f172a',
    lineHeight: 22,
  },
  levelLabel: {
    fontFamily: 'SpaceGrotesk_700Bold',
    fontSize: 8,
    color: 'rgba(0,0,0,0.5)',
    letterSpacing: 1,
  },
  centerBlock: {
    flex: 1,
    marginRight: 10,
  },
  topRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  archetypeText: {
    fontFamily: 'SpaceGrotesk_500Medium',
    fontSize: 9,
    color: COLORS.primary,
    letterSpacing: 1.5,
  },
  xpText: {
    fontFamily: 'SpaceGrotesk_700Bold',
    fontSize: 12,
    color: COLORS.text,
  },
  xpDim: {
    color: COLORS.textDim,
    fontFamily: 'SpaceGrotesk_500Medium',
  },
  barTrack: {
    height: 8,
    backgroundColor: 'rgba(255,255,255,0.06)',
    borderRadius: 4,
    overflow: 'hidden',
    position: 'relative',
  },
  barFill: {
    height: '100%',
    backgroundColor: COLORS.primary,
    borderRadius: 4,
    position: 'absolute',
  },
  barGlow: {
    height: '100%',
    backgroundColor: COLORS.primary,
    borderRadius: 4,
    position: 'absolute',
    shadowColor: COLORS.primary,
    shadowOffset: { width: 0, height: 0 },
    shadowRadius: 8,
  },
  statsBlock: {
    alignItems: 'flex-end',
  },
  statChip: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.04)',
    borderRadius: 10,
    paddingHorizontal: 8,
    paddingVertical: 3,
  },
  statEmoji: {
    fontSize: 12,
    marginRight: 4,
  },
  statChipText: {
    fontFamily: 'SpaceGrotesk_700Bold',
    fontSize: 13,
    color: COLORS.text,
  },
});
