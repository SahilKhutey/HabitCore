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
    const hapticMap = {
      xp: { type: 'impact', style: Haptics.ImpactFeedbackStyle.Medium },
      coins: { type: 'impact', style: Haptics.ImpactFeedbackStyle.Light },
      streak: { type: 'impact', style: Haptics.ImpactFeedbackStyle.Heavy },
      level: { type: 'notification', style: Haptics.NotificationFeedbackType.Success }
    };

    const config = hapticMap[type];
    if (config.type === 'impact') {
      Haptics.impactAsync(config.style as Haptics.ImpactFeedbackStyle);
    } else {
      Haptics.notificationAsync(config.style as Haptics.NotificationFeedbackType);
    }

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
