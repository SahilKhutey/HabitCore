import { useState, useCallback } from 'react';
import { soundEngine } from '../services/SoundEngine';
import { createAnticipation } from '../utils/delayReward';

export const useRewardSystem = () => {
  const [activeRewards, setActiveRewards] = useState<{
    xpBursts: Array<{ id: string; value: number; x: number; y: number }>;
    rewardBoxes: Array<{ id: string; reward: number; x: number; y: number }>;
    combos: Array<{ id: string; count: number; x: number; y: number }>;
    confetti: boolean;
    coins: Array<{ id: string; startX: number; startY: number; endX: number; endY: number }>;
  }>({
    xpBursts: [],
    rewardBoxes: [],
    combos: [],
    confetti: false,
    coins: []
  });

  const triggerConfetti = useCallback(() => {
    setActiveRewards(prev => ({ ...prev, confetti: true }));
    setTimeout(() => {
      setActiveRewards(prev => ({ ...prev, confetti: false }));
    }, 2000);
  }, []);

  const addXPBurst = useCallback((value: number, position: { x: number; y: number }) => {
    const id = Date.now().toString() + Math.random();
    setActiveRewards(prev => ({
      ...prev,
      xpBursts: [...prev.xpBursts, { id, value, x: position.x, y: position.y }]
    }));
  }, []);

  const addRewardBox = useCallback((position: { x: number; y: number }) => {
    const id = Date.now().toString() + Math.random();
    const reward = Math.floor(Math.random() * 50) + 25; // 25-75 XP
    
    setActiveRewards(prev => ({
      ...prev,
      rewardBoxes: [...prev.rewardBoxes, { id, reward, x: position.x, y: position.y }]
    }));
  }, []);

  const addCombo = useCallback((count: number, position: { x: number; y: number }) => {
    const id = Date.now().toString() + Math.random();
    
    setActiveRewards(prev => ({
      ...prev,
      combos: [...prev.combos, { id, count, x: position.x, y: position.y }]
    }));
  }, []);

  const addCoins = useCallback((count: number, startX: number, startY: number, endX: number, endY: number) => {
    const newCoins = Array.from({ length: count }).map((_, i) => ({
      id: (Date.now() + i).toString(),
      startX,
      startY,
      endX,
      endY
    }));

    setActiveRewards(prev => ({
      ...prev,
      coins: [...prev.coins, ...newCoins]
    }));

    setTimeout(() => {
      setActiveRewards(prev => ({
        ...prev,
        coins: prev.coins.filter(coin => !newCoins.find(c => c.id === coin.id))
      }));
    }, 1200);
  }, []);

  const triggerHabitCompletion = useCallback(async (habit: any, result: any, position: { x: number; y: number }) => {
    // Initial feedback
    await soundEngine.play('click');
    
    // Create anticipation
    await createAnticipation();
    
    // Base XP reward from backend result
    const xpReward = result.rewards?.total_xp || 10;
    addXPBurst(xpReward, position);
    
    // Coin sound and animation
    await soundEngine.play('coin');
    addCoins(5, position.x, position.y, 320, 40);
    
    // Check for combo (every 3 days)
    if (result.user_state?.current_streak % 3 === 0) {
      addCombo(result.user_state.current_streak, position);
    }
    
    // Random reward box (10% chance)
    if (Math.random() < 0.1) {
      addRewardBox({ x: position.x + 50, y: position.y - 50 });
    }
    
    // Celebration for streaks
    if (result.user_state?.current_streak % 7 === 0) {
      triggerConfetti();
      await soundEngine.play('streak');
    }

    // Level up
    if (result.user_state?.level_up) {
      triggerConfetti();
      await soundEngine.play('level_up');
    }
  }, [addXPBurst, addCoins, addCombo, addRewardBox, triggerConfetti]);

  const removeReward = useCallback((type: keyof typeof activeRewards, id: string) => {
    setActiveRewards(prev => ({
      ...prev,
      [type]: (prev[type] as any[]).filter((item: any) => item.id !== id)
    }));
  }, []);

  return {
    activeRewards,
    triggerHabitCompletion,
    addXPBurst,
    addRewardBox,
    addCombo,
    triggerConfetti,
    removeReward
  };
};
