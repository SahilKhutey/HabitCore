import React, { useEffect } from 'react';
import { StyleSheet, Dimensions } from 'react-native';
import Animated, { 
  useSharedValue, 
  useAnimatedStyle, 
  withTiming,
  withDelay,
  withSpring,
  Easing 
} from 'react-native-reanimated';

const { width, height } = Dimensions.get('window');

interface ConfettiParticleProps {
  id: number;
  emoji: string;
  delay: number;
}

function ConfettiParticle({ id, emoji, delay }: ConfettiParticleProps) {
  const y = useSharedValue(height);
  const x = useSharedValue(width / 2);
  const rotation = useSharedValue(0);
  const opacity = useSharedValue(0);
  const scale = useSharedValue(0);

  useEffect(() => {
    const randomX = Math.random() * width;
    const randomY = -height * (0.2 + Math.random() * 0.3);
    const randomRotation = Math.random() * 360;

    opacity.value = withDelay(delay, withTiming(1, { duration: 200 }));
    scale.value = withDelay(delay, withSpring(1, { damping: 15 }));
    
    y.value = withDelay(
      delay,
      withTiming(randomY, { 
        duration: 1200 + Math.random() * 600,
        easing: Easing.out(Easing.quad)
      })
    );
    
    x.value = withDelay(
      delay,
      withTiming(randomX, { 
        duration: 1200 + Math.random() * 600,
        easing: Easing.inOut(Easing.quad)
      })
    );
    
    rotation.value = withDelay(
      delay,
      withTiming(randomRotation, { 
        duration: 1000,
        easing: Easing.linear
      })
    );

    // Cleanup
    setTimeout(() => {
      opacity.value = withTiming(0, { duration: 300 });
    }, delay + 1000);

  }, []);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [
      { translateX: x.value },
      { translateY: y.value },
      { rotate: `${rotation.value}deg` },
      { scale: scale.value }
    ],
    opacity: opacity.value
  }));

  return (
    <Animated.Text style={[styles.particle, animatedStyle]}>
      {emoji}
    </Animated.Text>
  );
}

interface ConfettiExplosionProps {
  visible: boolean;
  intensity?: number;
}

export default function ConfettiExplosion({ visible, intensity = 20 }: ConfettiExplosionProps) {
  if (!visible) return null;

  const particles = ['🎉', '✨', '🌟', '🎊', '🥳', '💫', '⚡', '🔥'];
  
  return (
    <>
      {Array.from({ length: intensity }).map((_, index) => (
        <ConfettiParticle
          key={index}
          id={index}
          emoji={particles[Math.floor(Math.random() * particles.length)]}
          delay={index * 50}
        />
      ))}
    </>
  );
}

const styles = StyleSheet.create({
  particle: {
    fontSize: 24,
    position: 'absolute',
    zIndex: 998,
    textShadowColor: 'rgba(255, 255, 255, 0.8)',
    textShadowOffset: { width: 0, height: 0 },
    textShadowRadius: 2,
  }
});
