import React, { useEffect } from 'react';
import { View, StyleSheet } from 'react-native';
import Animated, { 
  useSharedValue, 
  useAnimatedStyle, 
  withSequence,
  withTiming,
  withDelay,
  Easing,
  runOnJS
} from 'react-native-reanimated';
import LottieView from 'lottie-react-native';
import { soundEngine } from '../services/SoundEngine';

interface AvatarEvolutionAnimationProps {
  visible: boolean;
  onComplete?: () => void;
}

export default function AvatarEvolutionAnimation({ visible, onComplete }: AvatarEvolutionAnimationProps) {
  const scale = useSharedValue(0);
  const opacity = useSharedValue(0);

  useEffect(() => {
    if (visible) {
      soundEngine.play('level_up', { volume: 1.0 });
      
      scale.value = withSequence(
        withTiming(1.5, { duration: 300, easing: Easing.out(Easing.cubic) }),
        withTiming(1, { duration: 200, easing: Easing.in(Easing.cubic) })
      );
      
      opacity.value = withSequence(
        withTiming(1, { duration: 300 }),
        withDelay(1500, withTiming(0, { duration: 500 }))
      );

      const timeout = setTimeout(() => {
        if (onComplete) runOnJS(onComplete)();
      }, 2000);

      return () => clearTimeout(timeout);
    }
  }, [visible, onComplete]);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
    opacity: opacity.value,
  }));

  if (!visible) return null;

  return (
    <View style={styles.container} pointerEvents="none">
      <Animated.View style={[styles.animationContainer, animatedStyle]}>
        {/* Placeholder for Lottie - in production use a real JSON file */}
        <LottieView
          source={{ uri: 'https://assets9.lottiefiles.com/packages/lf20_tou9ypsf.json' }}
          autoPlay
          loop={false}
          style={styles.lottie}
        />
      </Animated.View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    ...StyleSheet.absoluteFillObject,
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 10000,
  },
  animationContainer: {
    width: 300,
    height: 300,
    alignItems: 'center',
    justifyContent: 'center',
  },
  lottie: {
    width: 250,
    height: 250,
  }
});
