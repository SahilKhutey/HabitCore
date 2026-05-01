import { useState, useCallback } from 'react';
import { useRewardAnimation } from '../animations/useRewardAnimation';
import * as Haptics from 'expo-haptics';

export const useAnimationOrchestrator = () => {
  const [activeAnimations, setActiveAnimations] = useState<{
    xpBursts: Array<{ id: number; value: number; x: number; y: number }>;
    coins: Array<{ id: number; startX: number; startY: number; endX: number; endY: number }>;
    confetti: boolean;
  }>({
    xpBursts: [],
    coins: [],
    confetti: false
  });

  const { trigger: triggerReward } = useRewardAnimation();

  const triggerXPBurst = useCallback((value: number, x: number, y: number) => {
    const id = Date.now() + Math.random();
    setActiveAnimations(prev => ({
      ...prev,
      xpBursts: [...prev.xpBursts, { id, value, x, y }]
    }));

    // Remove after animation completes
    setTimeout(() => {
      setActiveAnimations(prev => ({
        ...prev,
        xpBursts: prev.xpBursts.filter(burst => burst.id !== id)
      }));
    }, 1200);

    triggerReward('xp');
  }, [triggerReward]);

  const triggerCoinFly = useCallback((count: number, startX: number, startY: number, endX: number, endY: number) => {
    const newCoins = Array.from({ length: count }).map((_, i) => ({
      id: Date.now() + i,
      startX,
      startY,
      endX,
      endY
    }));

    setActiveAnimations(prev => ({
      ...prev,
      coins: [...prev.coins, ...newCoins]
    }));

    // Remove after animation completes
    setTimeout(() => {
      setActiveAnimations(prev => ({
        ...prev,
        coins: prev.coins.filter(coin => !newCoins.find(c => c.id === coin.id))
      }));
    }, 1000);

    triggerReward('coins');
  }, [triggerReward]);

  const triggerConfetti = useCallback(() => {
    setActiveAnimations(prev => ({ ...prev, confetti: true }));
    setTimeout(() => {
      setActiveAnimations(prev => ({ ...prev, confetti: false }));
    }, 2000);

    Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
  }, []);

  const triggerLevelUp = useCallback(() => {
    triggerConfetti();
    triggerReward('level');
  }, [triggerConfetti, triggerReward]);

  const triggerStreak = useCallback((streak: number) => {
    triggerConfetti();
    triggerReward('streak');
  }, [triggerConfetti, triggerReward]);

  return {
    activeAnimations,
    triggerXPBurst,
    triggerCoinFly,
    triggerConfetti,
    triggerLevelUp,
    triggerStreak
  };
};
