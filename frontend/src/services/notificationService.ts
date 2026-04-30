import * as Notifications from "expo-notifications";
import { Platform } from "react-native";

export const setupNotifications = async () => {
  if (Platform.OS === 'web') return;

  const { status: existingStatus } = await Notifications.getPermissionsAsync();
  let finalStatus = existingStatus;
  
  if (existingStatus !== 'granted') {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }
  
  if (finalStatus !== 'granted') {
    console.log('Failed to get push token for push notification!');
    return;
  }

  Notifications.setNotificationHandler({
    handleNotification: async () => ({
      shouldShowAlert: true,
      shouldPlaySound: true,
      shouldSetBadge: false,
      shouldShowBanner: true,
      shouldShowList: true,
    }),
  });
};

export const scheduleHabitReminder = async (habit: { id: string; name: string; time: string | null }) => {
  if (Platform.OS === 'web' || !habit.time) return;

  // Cancel any existing reminder for this habit (using id as identifier)
  await cancelHabitReminder(habit.id);

  let hour = 9;
  if (habit.time === "Morning") hour = 8;
  if (habit.time === "Afternoon") hour = 14;
  if (habit.time === "Night") hour = 20;

  await Notifications.scheduleNotificationAsync({
    content: {
      title: "⏰ Habit Reminder",
      body: `Time for: ${habit.name}`,
      data: { habitId: habit.id },
    },
    trigger: {
      hour,
      minute: 0,
      repeats: true,
    } as any,
    identifier: habit.id, // Use habit ID to manage uniquely
  });
  
  console.log(`Scheduled reminder for ${habit.name} at ${hour}:00`);
};

export const scheduleSmartReminder = async (habitId: string, habitName: string, token: string) => {
  if (Platform.OS === 'web') return;

  try {
    const { getSmartTime } = require("../api/client");
    const res = await getSmartTime(habitId, token);
    const hour = res.hour;

    await cancelHabitReminder(habitId);

    await Notifications.scheduleNotificationAsync({
      content: {
        title: "⏰ Smart Reminder",
        body: `Time for your habit: ${habitName}`,
        data: { habitId },
      },
      trigger: {
        hour,
        minute: 0,
        repeats: true,
      } as any,
      identifier: habitId,
    });
    
    console.log(`Scheduled smart reminder for ${habitName} at ${hour}:00`);
  } catch (err) {
    console.log("Failed to schedule smart reminder", err);
  }
};

export const cancelHabitReminder = async (habitId: string) => {
  if (Platform.OS === 'web') return;
  await Notifications.cancelScheduledNotificationAsync(habitId);
};
