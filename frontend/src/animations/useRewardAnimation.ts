import { useSharedValue, withTiming, withSpring, runOnJS } from 'react-native-reanimated';
import * as Haptics from 'expo-haptics';
import { useState, useCallback } from 'react';

export const useRewardAnimation = () => {
  const [isAnimating, setIsAnimating] = useState(false);
  const scale = useSharedValue(0);
  const opacity = useSharedValue(0);
  const rotation = useSharedValue(0);
  const particles = useSharedValue(0);

  const trigger = useCallback((type: 'xp' | 'coins' | 'streak' | 'level') => {
    if (isAnimating) return;
    
    setIsAnimating(true);
    
    // Different haptic feedback for different rewards
    const hapticType = {
      xp: Haptics.ImpactFeedbackStyle.Medium,
      coins: Haptics.ImpactFeedbackStyle.Light,
      streak: Haptics.ImpactFeedbackStyle.Heavy,
      level: Haptics.NotificationFeedbackType.Success
    }[type];

    Haptics.impactAsync(hapticType);

    // Entry animation
    scale.value = withSpring(1.2, { damping: 10, stiffness: 100 });
    opacity.value = withTiming(1, { duration: 200 });
    rotation.value = withTiming(360, { duration: 800 });
    particles.value = withTiming(1, { duration: 400 });

    // Exit animation
    setTimeout(() => {
      scale.value = withTiming(0, { duration: 300 });
      opacity.value = withTiming(0, { duration: 300 });
      runOnJS(setIsAnimating)(false);
    }, 1200);

  }, [isAnimating]);

  return { scale, opacity, rotation, particles, trigger, isAnimating };
};
