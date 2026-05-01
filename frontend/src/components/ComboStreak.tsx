import React, { useEffect } from 'react';
import { Text, StyleSheet } from 'react-native';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSequence,
  withTiming,
  runOnJS
} from 'react-native-reanimated';
import { soundEngine } from '../services/SoundEngine';
import { COLORS, TYPOGRAPHY } from '../theme/theme';

interface ComboStreakProps {
  count: number;
  position: { x: number; y: number };
  onComplete?: () => void;
}

export default function ComboStreak({ count, position, onComplete }: ComboStreakProps) {
  const scale = useSharedValue(0);
  const opacity = useSharedValue(0);

  useEffect(() => {
    soundEngine.play('combo', { volume: 1.0 });
    
    // Pop-in animation
    scale.value = withSequence(
      withTiming(1.2, { duration: 200 }),
      withTiming(0.9, { duration: 100 }),
      withTiming(1, { duration: 100 })
    );
    
    opacity.value = withTiming(1, { duration: 200 });

    // Hold and fade out
    const timeout = setTimeout(() => {
      opacity.value = withTiming(0, { duration: 500 });
      setTimeout(() => {
        if (onComplete) runOnJS(onComplete)();
      }, 500);
    }, 1500);

    return () => clearTimeout(timeout);
  }, [onComplete]);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
    opacity: opacity.value,
  }));

  return (
    <Animated.View
      style={[
        styles.container,
        { left: position.x, top: position.y },
        animatedStyle
      ]}
    >
      <Text style={styles.comboText}>
        🔥 x{count} COMBO!
      </Text>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    backgroundColor: 'rgba(245, 158, 11, 0.9)',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    borderWidth: 2,
    borderColor: 'rgba(255, 255, 255, 0.3)',
    zIndex: 1002,
  },
  comboText: {
    ...TYPOGRAPHY.h2,
    color: COLORS.text,
    fontWeight: 'bold',
  }
});
