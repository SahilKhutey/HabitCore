import { Platform } from 'react-native';
let Haptics: any;
if (Platform.OS !== 'web') {
  try {
    Haptics = require('expo-haptics');
  } catch (e) {
    Haptics = null;
  }
}

export type RewardType = "xp" | "coins" | "level_up" | "streak" | "success" | "error";

export const triggerHaptic = (type: RewardType) => {
  if (!Haptics) return;
  
  switch (type) {
    case "xp":
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
      break;
    case "coins":
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
      break;
    case "level_up":
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      break;
    case "streak":
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy);
      break;
    case "success":
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      break;
    case "error":
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
      break;
  }
};

export const getRewardConfig = (type: RewardType) => {
  switch (type) {
    case "xp":
      return { animation: "floatUp", color: "#00ffcc" };
    case "coins":
      return { animation: "bounce", color: "#eab308" };
    case "level_up":
      return { animation: "confetti", color: "#a855f7" };
    case "streak":
      return { animation: "fire", color: "#f59e0b" };
  }
};
