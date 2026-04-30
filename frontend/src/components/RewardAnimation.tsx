import React, { useEffect } from 'react';
import { View, StyleSheet, Text } from 'react-native';
import Animated, { 
  useSharedValue, 
  useAnimatedStyle, 
  withSpring, 
  withSequence, 
  withDelay,
  withTiming,
  runOnJS
} from 'react-native-reanimated';
import { COLORS } from '../theme/theme';

interface RewardAnimationProps {
  visible: boolean;
  onFinish: () => void;
  xpAmount: number;
}

export const RewardAnimation: React.FC<RewardAnimationProps> = ({ visible, onFinish, xpAmount }) => {
  const opacity = useSharedValue(0);
  const scale = useSharedValue(0);
  const translateY = useSharedValue(0);

  useEffect(() => {
    if (visible) {
      opacity.value = withSequence(
        withTiming(1, { duration: 200 }),
        withDelay(800, withTiming(0, { duration: 500 }))
      );
      scale.value = withSpring(1);
      translateY.value = withSequence(
        withTiming(-50, { duration: 1000 }),
        withTiming(-100, { duration: 500 })
      );
      
      setTimeout(() => {
        runOnJS(onFinish)();
      }, 1500);
    }
  }, [visible]);

  const animatedStyle = useAnimatedStyle(() => ({
    opacity: opacity.value,
    transform: [
      { scale: scale.value },
      { translateY: translateY.value }
    ],
  }));

  if (!visible) return null;

  return (
    <View style={styles.container} pointerEvents="none">
      <Animated.View style={[styles.burst, animatedStyle]}>
        <Text style={styles.xpText}>+{xpAmount} XP</Text>
        <Text style={styles.sparkle}>✨</Text>
      </Animated.View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    ...StyleSheet.absoluteFillObject,
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 999,
  },
  burst: {
    backgroundColor: COLORS.primary,
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 30,
    flexDirection: 'row',
    alignItems: 'center',
    shadowColor: COLORS.primary,
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.5,
    shadowRadius: 20,
    elevation: 10,
  },
  xpText: {
    color: '#FFF',
    fontSize: 24,
    fontWeight: '800',
  },
  sparkle: {
    fontSize: 24,
    marginLeft: 8,
  },
});
