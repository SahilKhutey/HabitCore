import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  FlatList,
  StyleSheet,
  SafeAreaView,
  ActivityIndicator,
  RefreshControl,
  Alert
} from "react-native";
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withTiming,
  FadeInUp
} from "react-native-reanimated";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api, getTodayStatus, deleteHabit, getRecommendations, adjustDifficulty } from "../../api/client";
import { useUserStore } from "../../store/useUserStore";
import { HabitCard } from "../../components/HabitCard";
import { triggerHaptic } from "../../utils/animationManager";
import { COLORS } from "../../theme/theme";
import { setupNotifications, cancelHabitReminder, scheduleSmartReminder } from "../../services/notificationService";
import { Brain } from "lucide-react-native";

export default function HomeScreen({ navigation }: any) {
  const { token, id, xp, level, coins } = useUserStore();
  const queryClient = useQueryClient();
  const [optimisticCompleted, setOptimisticCompleted] = useState<string[]>([]);

  const { data: habits, isLoading, refetch } = useQuery({
    queryKey: ['habits', id],
    queryFn: () => api(`/habits/${id}`, 'GET', null, token),
    enabled: !!id && !!token,
  });

  const { data: completedIds = [] } = useQuery({
    queryKey: ['todayStatus', id],
    queryFn: () => getTodayStatus(token!),
    enabled: !!id && !!token,
  });

  const { data: recommendations } = useQuery({
    queryKey: ['recommendations', id],
    queryFn: () => getRecommendations(token!),
    enabled: !!id && !!token,
  });

  const completeMutation = useMutation({
    mutationFn: (habitId: string) => api(`/habits/complete`, 'POST', { habit_id: habitId }, token),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['habits'] });
      queryClient.invalidateQueries({ queryKey: ['todayStatus'] });
      useUserStore.getState().setUserInfo({ 
        xp: data.xp, 
        level: data.level,
        coins: data.coins 
      });

      // Adaptive Learning: Update smart reminder on completion
      const completedHabit = habits?.find((h: any) => h.id === data.habit_id);
      if (completedHabit) {
        scheduleSmartReminder(data.habit_id, completedHabit.name || completedHabit.title, token!);
        triggerAdjustmentCheck(data.habit_id, completedHabit.name || completedHabit.title);
      }
    },
  });

  const progress = habits?.length 
    ? (habits.filter((h: any) => completedIds.includes(h.id) || optimisticCompleted.includes(h.id)).length / habits.length)
    : 0;

  // Progress animation
  const progressWidth = useSharedValue(0);
  
  useEffect(() => {
    setupNotifications();
  }, []);

  useEffect(() => {
    progressWidth.value = withTiming(progress * 100, { duration: 400 });
  }, [progress]);

  const progressStyle = useAnimatedStyle(() => ({
    width: `${progressWidth.value}%`,
  }));

  const completeHabit = (habitId: string) => {
    setOptimisticCompleted(prev => [...prev, habitId]);
    completeMutation.mutate(habitId);
    triggerHaptic("xp");
  };

  const triggerAdjustmentCheck = async (habitId: string, habitName: string) => {
    try {
      const res = await adjustDifficulty(habitId, token!);
      if (res.status === "success" && res.change) {
        const title = res.change === "increase" ? "Level Up? 🔥" : "Adjust Pace? 🧘";
        const message = res.change === "increase" 
            ? `You're crushing "${habitName}"! Want to increase difficulty to ${res.difficulty}?`
            : `Let's make "${habitName}" a bit easier to stay consistent. Set to ${res.difficulty}?`;

        Alert.alert(title, message, [
          { text: "Keep Current", style: "cancel" },
          { text: res.change === "increase" ? "Try Harder" : "Make Easier", onPress: () => {
             queryClient.invalidateQueries({ queryKey: ["habits"] });
             triggerHaptic("level_up");
          }}
        ]);
      }
    } catch (err) {
      console.log("Adjustment check failed", err);
    }
  };

  const handleEdit = (habit: any) => {
    navigation.navigate("AddHabit", { habit });
  };

  const handleViewDetail = (habit: any) => {
    navigation.navigate("HabitDetail", { habit });
  };

  const handleDelete = async (habitId: string) => {
    try {
      await deleteHabit(habitId, token!);
      await cancelHabitReminder(habitId);
      queryClient.invalidateQueries({ queryKey: ["habits"] });
      triggerHaptic("coins");
    } catch (err) {
      alert("Failed to delete habit");
    }
  };

  if (isLoading && !habits) {
    return (
      <View style={[styles.container, { justifyContent: 'center' }]}>
        <ActivityIndicator color="#00ffcc" />
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={{ padding: 20, flex: 1 }}>
        {/* 🔥 STREAK */}
        <Text style={styles.streak}>🔥 5 Day Streak</Text>

        {/* 📊 PROGRESS */}
        <View style={styles.progressContainer}>
          <Animated.View style={[styles.progressBar, progressStyle]} />
        </View>

        {/* 🤖 SMART INSIGHT */}
        {recommendations?.insights?.[0] && (
          <Animated.View entering={FadeInUp} style={styles.insightCard}>
            <Brain size={18} color="#00ffcc" />
            <Text style={styles.insightText}>{recommendations.insights[0]}</Text>
          </Animated.View>
        )}

        {/* 🎯 HABITS */}
        <Text style={styles.section}>Today</Text>

        <FlatList
          data={habits || []}
          keyExtractor={(item) => item.id}
          showsVerticalScrollIndicator={false}
          refreshControl={
            <RefreshControl refreshing={isLoading} onRefresh={refetch} tintColor="#00ffcc" />
          }
          renderItem={({ item }) => (
            <HabitCard 
                item={{ 
                    ...item, 
                    done: completedIds.includes(item.id) || optimisticCompleted.includes(item.id) 
                }} 
                onComplete={completeHabit} 
                onEdit={handleEdit}
                onDelete={handleDelete}
                onViewDetail={handleViewDetail}
            />
          )}
        />

        {/* ➕ ADD HABIT */}
        <TouchableOpacity 
          style={styles.addBtn}
          onPress={() => navigation.navigate("AddHabit")}
        >
          <Text style={{ color: "#000", fontWeight: '700' }}>+ Add Habit</Text>
        </TouchableOpacity>

        {/* 💰 FOOTER */}
        <View style={styles.footer}>
          <Text style={styles.coins}>💰 {coins}</Text>
          <TouchableOpacity onPress={() => navigation.navigate("Shop")}>
            <Text style={styles.shop}>🛒 Shop</Text>
          </TouchableOpacity>
        </View>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#000",
  },

  streak: {
    color: "#ff5500",
    fontSize: 20,
    fontWeight: '900',
    marginBottom: 10,
    marginTop: 10,
  },

  progressContainer: {
    height: 10,
    backgroundColor: "#222",
    borderRadius: 10,
    overflow: "hidden",
    marginBottom: 20,
  },

  progressBar: {
    height: "100%",
    backgroundColor: "#00ffcc",
  },

  insightCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#111',
    padding: 15,
    borderRadius: 16,
    marginBottom: 25,
    gap: 12,
    borderWidth: 1,
    borderColor: 'rgba(0, 255, 204, 0.1)',
  },

  insightText: {
    color: '#00ffcc',
    fontSize: 14,
    fontWeight: '600',
    flex: 1,
  },

  section: {
    color: "#fff",
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 15,
  },

  addBtn: {
    backgroundColor: "#00ffcc",
    padding: 16,
    borderRadius: 16,
    alignItems: "center",
    marginTop: 10,
  },

  footer: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginTop: 20,
    paddingBottom: 10,
  },

  coins: {
    color: "#ffd700",
    fontSize: 16,
    fontWeight: '700',
  },

  shop: {
    color: "#00ffcc",
    fontSize: 16,
    fontWeight: '700',
  },
});
