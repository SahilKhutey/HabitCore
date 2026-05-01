import { soundEngine } from '../services/SoundEngine';

export const delayReward = (callback: () => void, delayMs: number = 300): Promise<void> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      callback();
      resolve();
    }, delayMs);
  });
};

export const createAnticipation = async (): Promise<void> => {
  // Play anticipation sound/haptic
  await soundEngine.play('click', { volume: 0.5, haptic: false });
  
  // Return promise that resolves after delay
  return new Promise(resolve => setTimeout(resolve, 300));
};
