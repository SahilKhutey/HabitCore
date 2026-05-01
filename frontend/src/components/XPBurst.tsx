import React, { useEffect } from 'react';
import { StyleSheet } from 'react-native';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withTiming,
  withSequence,
  withDelay,
  runOnJS
} from 'react-native-reanimated';
import { COLORS, TYPOGRAPHY } from '../theme/theme';

interface XPBurstProps {
  value: number;
  position: { x: number; y: number };
  onComplete?: () => void;
  delay?: number;
}

export default function XPBurst({ value, position, onComplete, delay = 0 }: XPBurstProps) {
  const translateY = useSharedValue(0);
  const opacity = useSharedValue(0);
  const scale = useSharedValue(0.5);

  useEffect(() => {
    // Entry animation
    opacity.value = withDelay(delay, withTiming(1, { duration: 200 }));
    scale.value = withDelay(delay, withTiming(1, { duration: 300 }));
    
    // Rise animation with bounce effect
    translateY.value = withDelay(
      delay,
      withSequence(
        withTiming(-20, { duration: 300 }),
        withTiming(-40, { duration: 200 }),
        withTiming(-50, { duration: 100 })
      )
    );

    // Fade out
    opacity.value = withDelay(
      delay + 600,
      withTiming(0, { duration: 400 })
    );

    // Complete callback
    const timeout = setTimeout(() => {
      if (onComplete) runOnJS(onComplete)();
    }, delay + 1000);

    return () => clearTimeout(timeout);
  }, [delay, onComplete]);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [
      { translateY: translateY.value },
      { translateX: position.x },
      { scale: scale.value }
    ],
    opacity: opacity.value,
  }));

  return (
    <Animated.Text
      style={[
        styles.xpText,
        { top: position.y },
        animatedStyle
      ]}
      numberOfLines={1}
    >
      +{value} XP
    </Animated.Text>
  );
}

const styles = StyleSheet.create({
  xpText: {
    ...TYPOGRAPHY.h2,
    color: COLORS.primary,
    fontWeight: 'bold',
    position: 'absolute',
    textShadowColor: 'rgba(0, 255, 204, 0.8)',
    textShadowOffset: { width: 0, height: 0 },
    textShadowRadius: 10,
    zIndex: 1000,
  }
});
