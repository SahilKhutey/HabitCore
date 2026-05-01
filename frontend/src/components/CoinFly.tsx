import React, { useEffect } from 'react';
import { StyleSheet } from 'react-native';
import Animated, { 
  useSharedValue, 
  useAnimatedStyle, 
  withTiming,
  withDelay,
  withSpring,
  Easing 
} from 'react-native-reanimated';

interface CoinFlyProps {
  id: number;
  startX: number;
  startY: number;
  endX: number;
  endY: number;
  delay?: number;
  onComplete?: () => void;
}

export default function CoinFly({ 
  id, 
  startX, 
  startY, 
  endX, 
  endY, 
  delay = 0,
  onComplete 
}: CoinFlyProps) {
  const x = useSharedValue(startX);
  const y = useSharedValue(startY);
  const opacity = useSharedValue(0);
  const scale = useSharedValue(0.5);

  useEffect(() => {
    // Staggered entry
    opacity.value = withDelay(delay, withTiming(1, { duration: 200 }));
    scale.value = withDelay(delay, withSpring(1, { damping: 12 }));

    // Flying animation
    x.value = withDelay(
      delay + 100,
      withTiming(endX, { 
        duration: 800,
        easing: Easing.out(Easing.quad)
      })
    );
    
    y.value = withDelay(
      delay + 100,
      withTiming(endY, { 
        duration: 800,
        easing: Easing.in(Easing.quad)
      })
    );

    // Fade out at destination
    setTimeout(() => {
      opacity.value = withTiming(0, { duration: 200 });
      scale.value = withTiming(0.5, { duration: 200 });
      onComplete?.();
    }, delay + 900);

  }, []);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [
      { translateX: x.value },
      { translateY: y.value },
      { scale: scale.value }
    ],
    opacity: opacity.value
  }));

  return (
    <Animated.Text 
      style={[styles.coin, animatedStyle]}
      pointerEvents="none"
    >
      🪙
    </Animated.Text>
  );
}

const styles = StyleSheet.create({
  coin: {
    fontSize: 24,
    position: 'absolute',
    zIndex: 999,
  }
});
