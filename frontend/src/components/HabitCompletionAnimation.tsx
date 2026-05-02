import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import Animated, { 
  withSpring, 
  withSequence,
  withDelay,
  useSharedValue,
  useAnimatedStyle,
  interpolateColor,
  FadeIn,
  FadeOut
} from 'react-native-reanimated';
import * as Haptics from 'expo-haptics';
import { COLORS, SPACING, TYPOGRAPHY } from '../theme/theme';
import { Check, Zap } from 'lucide-react-native';
import { GlassCard } from './GlassCard';

interface Habit {
  id: string;
  name: string;
  difficulty: string;
  xp_reward?: number;
  duration?: string;
}

interface HabitCompletionAnimationProps {
  habit: Habit;
  onComplete: (habit: Habit) => Promise<any>;
  isHindi?: boolean;
}

export default function HabitCompletionAnimation({ habit, onComplete, isHindi = false }: HabitCompletionAnimationProps) {
  const [isCompleting, setIsCompleting] = useState(false);
  const [isDone, setIsDone] = useState(false);
  const [reward, setReward] = useState<any>(null);
  
  const scale = useSharedValue(1);
  const completionProgress = useSharedValue(0);

  const containerStyle = useAnimatedStyle(() => {
    const borderColor = interpolateColor(
      completionProgress.value,
      [0, 1],
      ['rgba(255, 255, 255, 0.1)', COLORS.primary]
    );

    return {
      transform: [{ scale: scale.value }],
      borderColor,
      backgroundColor: completionProgress.value > 0.5 ? 'rgba(0, 255, 204, 0.15)' : 'transparent',
    };
  });

  const glowStyle = useAnimatedStyle(() => ({
    opacity: completionProgress.value,
    shadowColor: COLORS.primary,
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: completionProgress.value * 0.5,
    shadowRadius: 15,
  }));

  const handleComplete = async () => {
    if (isCompleting || isDone) return;
    setIsCompleting(true);
    
    // Animation sequence
    scale.value = withSequence(
      withSpring(0.95),
      withSpring(1.05),
      withSpring(1)
    );
    
    completionProgress.value = withSpring(1);

    try {
      const result = await onComplete(habit);
      
      if (result.success) {
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
        setReward(result.rewards);
        setIsDone(true);
        
        // Reset state after showing reward
        setTimeout(() => {
          setReward(null);
          setIsCompleting(false);
        }, 2500);
      } else {
        completionProgress.value = withSpring(0);
        setIsCompleting(false);
      }
    } catch (error) {
      console.error('Completion error:', error);
      completionProgress.value = withSpring(0);
      setIsCompleting(false);
    }
  };

  return (
    <View style={styles.wrapper}>
      <Animated.View style={[styles.glowLayer, glowStyle]} />
      <GlassCard 
        style={[styles.container, containerStyle]}
        variant={isDone ? 'highlighted' : 'default'}
      >
        <TouchableOpacity
          onPress={handleComplete}
          disabled={isCompleting || isDone}
          style={styles.button}
          activeOpacity={0.8}
        >
          <View style={styles.leftContent}>
            <View style={[styles.checkCircle, isDone && styles.checkCircleDone]}>
              {isDone ? (
                <Check color="#000" size={14} strokeWidth={3} />
              ) : (
                <Zap color={COLORS.primary} size={12} fill={COLORS.primary} />
              )}
            </View>
            <View>
              <Text style={[styles.habitName, isDone && styles.habitNameDone]}>
                {habit.name}
              </Text>
              <View style={styles.metaRow}>
                <Text style={styles.metaText}>{habit.duration || 'Daily'}</Text>
                <Text style={styles.dot}>•</Text>
                <Text style={styles.xpText}>+{habit.xp_reward || 50} XP</Text>
              </View>
            </View>
          </View>
          
          {!isDone && (
            <View style={styles.actionBtn}>
              <Text style={styles.actionText}>{isHindi ? 'पूरा करें' : 'DONE'}</Text>
            </View>
          )}
        </TouchableOpacity>
      </GlassCard>

      {reward && (
        <Animated.View 
          entering={FadeIn.duration(400)}
          exiting={FadeOut.duration(400)}
          style={styles.rewardOverlay}
        >
          <View style={styles.rewardCard}>
            <Text style={styles.rewardText}>+{reward.total_xp || 50} XP</Text>
            <Text style={styles.rewardSubtext}>
              {isHindi ? 'शानदार! 🔥' : 'LEVEL UP FLOW 🔥'}
            </Text>
          </View>
        </Animated.View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: { marginBottom: SPACING.md, position: 'relative' },
  glowLayer: {
    ...StyleSheet.absoluteFillObject,
    borderRadius: 20,
    backgroundColor: COLORS.primary,
    zIndex: -1,
  },
  container: {
    padding: 0, // Reset GlassCard padding for custom inner button
    borderWidth: 1.5,
  },
  button: { 
    padding: SPACING.lg, 
    flexDirection: 'row', 
    alignItems: 'center', 
    justifyContent: 'space-between' 
  },
  leftContent: { flexDirection: 'row', alignItems: 'center', flex: 1 },
  checkCircle: { 
    width: 32, 
    height: 32, 
    borderRadius: 16, 
    borderWidth: 1.5, 
    borderColor: 'rgba(0, 255, 204, 0.3)', 
    alignItems: 'center', 
    justifyContent: 'center',
    marginRight: SPACING.md,
    backgroundColor: 'rgba(0, 255, 204, 0.05)',
  },
  checkCircleDone: {
    backgroundColor: COLORS.primary,
    borderColor: COLORS.primary,
  },
  habitName: { 
    ...TYPOGRAPHY.h3, 
    color: COLORS.text,
  },
  habitNameDone: {
    opacity: 0.6,
    textDecorationLine: 'line-through',
  },
  metaRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 4,
  },
  metaText: {
    ...TYPOGRAPHY.caption,
    color: COLORS.textDim,
  },
  dot: {
    color: COLORS.textDim,
    marginHorizontal: 6,
    fontSize: 10,
  },
  xpText: {
    ...TYPOGRAPHY.caption,
    color: COLORS.primary,
    fontWeight: '700',
  },
  actionBtn: {
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
  },
  actionText: {
    ...TYPOGRAPHY.label,
    fontSize: 10,
    color: COLORS.primary,
  },
  rewardOverlay: {
    position: 'absolute',
    top: -30,
    right: 0,
    left: 0,
    alignItems: 'center',
    zIndex: 10
  },
  rewardCard: {
    backgroundColor: COLORS.primary,
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 24,
    shadowColor: COLORS.primary,
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.4,
    shadowRadius: 12,
    elevation: 10
  },
  rewardText: { ...TYPOGRAPHY.h3, color: '#000' },
  rewardSubtext: { ...TYPOGRAPHY.caption, fontWeight: '700', color: '#000', textAlign: 'center' }
});
