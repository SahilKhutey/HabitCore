import React, { useState } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withTiming,
  withSequence,
  withSpring
} from 'react-native-reanimated';
import ButtonPressScale from './ButtonPressScale';
import { soundEngine } from '../services/SoundEngine';
import { delayReward } from '../utils/delayReward';
import { COLORS, TYPOGRAPHY } from '../theme/theme';

interface RewardBoxProps {
  reward: number;
  onReveal?: (reward: number) => void;
  position?: { x: number; y: number };
}

export default function RewardBox({ reward, onReveal, position }: RewardBoxProps) {
  const [isOpened, setIsOpened] = useState(false);
  const [isRevealing, setIsRevealing] = useState(false);
  const scale = useSharedValue(1);
  const rotation = useSharedValue(0);

  const handleOpen = async () => {
    if (isOpened || isRevealing) return;

    setIsRevealing(true);
    
    // Play reveal sound with anticipation
    await soundEngine.play('reveal', { volume: 0.8 });
    
    // Shake animation
    scale.value = withSequence(
      withSpring(1.1),
      withSpring(0.95),
      withSpring(1.05),
      withSpring(1)
    );

    rotation.value = withSequence(
      withTiming(-10, { duration: 100 }),
      withTiming(10, { duration: 100 }),
      withTiming(-5, { duration: 50 }),
      withTiming(0, { duration: 50 })
    );

    // Anticipation delay
    await delayReward(() => {
      setIsOpened(true);
      setIsRevealing(false);
      soundEngine.play('reward', { volume: 1.0 });
      onReveal?.(reward);
    }, 500);
  };

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [
      { scale: scale.value },
      { rotate: `${rotation.value}deg` }
    ],
  }));

  return (
    <View style={[styles.container, position && { left: position.x, top: position.y }]}>
      <ButtonPressScale onPress={handleOpen} scaleTo={0.9}>
        <Animated.View style={[styles.box, animatedStyle]}>
          <Text style={styles.boxText}>
            {isOpened ? `+${reward} XP` : '🎁'}
          </Text>
          {!isOpened && (
            <Text style={styles.tapText}>Tap!</Text>
          )}
        </Animated.View>
      </ButtonPressScale>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    zIndex: 1001,
  },
  box: {
    backgroundColor: 'rgba(139, 92, 246, 0.9)',
    padding: 20,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 2,
    borderColor: 'rgba(255, 255, 255, 0.3)',
    minWidth: 80,
  },
  boxText: {
    ...TYPOGRAPHY.h2,
    color: COLORS.text,
    fontWeight: 'bold',
  },
  tapText: {
    ...TYPOGRAPHY.caption,
    color: COLORS.textSecondary,
    marginTop: 4,
  }
});
