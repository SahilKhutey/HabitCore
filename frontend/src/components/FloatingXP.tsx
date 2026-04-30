import React from 'react';
import { StyleSheet, Text } from 'react-native';
import Animated, { 
  useSharedValue, 
  useAnimatedStyle, 
  withTiming, 
  withSequence, 
  runOnJS,
  FadeOutUp
} from 'react-native-reanimated';
import { COLORS } from '../theme/theme';

interface FloatingXPProps {
  amount: number;
  onAnimationComplete: () => void;
}

export const FloatingXP: React.FC<FloatingXPProps> = ({ amount, onAnimationComplete }) => {
  const opacity = useSharedValue(1);
  const translateY = useSharedValue(0);

  const animatedStyle = useAnimatedStyle(() => ({
    opacity: opacity.value,
    transform: [{ translateY: translateY.value }],
  }));

  React.useEffect(() => {
    translateY.value = withTiming(-60, { duration: 600 });
    opacity.value = withSequence(
      withTiming(1, { duration: 100 }),
      withDelay(400, withTiming(0, { duration: 100 }, () => {
        runOnJS(onAnimationComplete)();
      }))
    );
  }, []);

  return (
    <Animated.View style={[styles.container, animatedStyle]} exiting={FadeOutUp}>
      <Text style={styles.text}>+{amount} XP ↑</Text>
    </Animated.View>
  );
};

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    top: 0,
    right: 20,
    zIndex: 1000,
  },
  text: {
    color: COLORS.secondary,
    fontWeight: '800',
    fontSize: 18,
    textShadowColor: 'rgba(0,0,0,0.5)',
    textShadowOffset: { width: 0, height: 1 },
    textShadowRadius: 2,
  },
});

import { withDelay } from 'react-native-reanimated';
