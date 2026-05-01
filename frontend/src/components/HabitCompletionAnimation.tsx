import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import Animated, { 
  withSpring, 
  withSequence,
  withDelay,
  useSharedValue,
  useAnimatedStyle,
  runOnJS,
  FadeIn,
  FadeOut
} from 'react-native-reanimated';
import * as Haptics from 'expo-haptics';
import { COLORS, SPACING, TYPOGRAPHY } from '../theme/theme';
import { Check } from 'lucide-react-native';

interface Habit {
  id: string;
  name: string;
  difficulty: string;
}

interface HabitCompletionAnimationProps {
  habit: Habit;
  onComplete: (habit: Habit) => Promise<any>;
  isHindi?: boolean;
}

export default function HabitCompletionAnimation({ habit, onComplete, isHindi = false }: HabitCompletionAnimationProps) {
  const [isCompleting, setIsCompleting] = useState(false);
  const [reward, setReward] = useState<any>(null);
  
  const scale = useSharedValue(1);
  const opacity = useSharedValue(1);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
    opacity: opacity.value
  }));

  const handleComplete = async () => {
    if (isCompleting) return;
    setIsCompleting(true);
    
    // Animation sequence
    scale.value = withSequence(
      withSpring(0.95),
      withSpring(1.1),
      withDelay(200, withSpring(1))
    );
    
    opacity.value = withSequence(
      withSpring(0.8),
      withDelay(300, withSpring(1))
    );

    try {
      const result = await onComplete(habit);
      
      if (result.success) {
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
        setReward(result.rewards);
        
        // Hide reward after delay
        setTimeout(() => {
          setReward(null);
          setIsCompleting(false);
        }, 2500);
      } else {
        setIsCompleting(false);
      }
    } catch (error) {
      console.error('Completion error:', error);
      setIsCompleting(false);
    }
  };

  return (
    <View style={styles.wrapper}>
      <Animated.View style={[styles.container, animatedStyle]}>
        <TouchableOpacity
          onPress={handleComplete}
          onPressIn={() => {
            scale.value = withSpring(0.95, { damping: 15 });
          }}
          onPressOut={() => {
            if (!isCompleting) {
              scale.value = withSpring(1, { damping: 15 });
            }
          }}
          disabled={isCompleting}
          style={styles.button}
          activeOpacity={0.7}
        >
          <View style={styles.content}>
            <View style={styles.checkCircle}>
              <Check color={COLORS.primary} size={16} />
            </View>
            <Text style={styles.habitName}>{habit.name}</Text>
          </View>
          <Text style={styles.difficulty}>{habit.difficulty.toUpperCase()}</Text>
        </TouchableOpacity>
      </Animated.View>

      {reward && (
        <Animated.View 
          entering={FadeIn.duration(400)}
          exiting={FadeOut.duration(400)}
          style={styles.rewardOverlay}
        >
          <View style={styles.rewardCard}>
            <Text style={styles.rewardText}>+{reward.total_xp} XP</Text>
            <Text style={styles.rewardSubtext}>
              {isHindi ? 'शानदार! 🔥' : 'AMAZING! 🔥'}
            </Text>
          </View>
        </Animated.View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: { marginBottom: 12, position: 'relative' },
  container: { borderRadius: 16, backgroundColor: COLORS.surface, elevation: 2 },
  button: { 
    padding: 16, 
    flexDirection: 'row', 
    alignItems: 'center', 
    justifyContent: 'space-between' 
  },
  content: { flexDirection: 'row', alignItems: 'center' },
  checkCircle: { 
    width: 24, 
    height: 24, 
    borderRadius: 12, 
    borderWidth: 2, 
    borderColor: COLORS.primary, 
    alignItems: 'center', 
    justifyContent: 'center',
    marginRight: 12
  },
  habitName: { ...TYPOGRAPHY.body, fontWeight: '600', color: COLORS.text },
  difficulty: { ...TYPOGRAPHY.caption, color: COLORS.textSecondary },
  rewardOverlay: {
    position: 'absolute',
    top: -20,
    right: 0,
    left: 0,
    alignItems: 'center',
    zIndex: 10
  },
  rewardCard: {
    backgroundColor: '#fbbf24',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    shadowColor: '#fbbf24',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.5,
    shadowRadius: 10,
    elevation: 8
  },
  rewardText: { ...TYPOGRAPHY.body, fontWeight: '900', color: '#000' },
  rewardSubtext: { ...TYPOGRAPHY.caption, fontWeight: '700', color: '#000', textAlign: 'center' }
});
