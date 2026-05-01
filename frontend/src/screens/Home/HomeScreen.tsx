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
import * as Sharing from "expo-sharing";
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withTiming,
  FadeInUp
} from "react-native-reanimated";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api, getTodayStatus, deleteHabit, getRecommendations, adjustDifficulty, useFreeze, getBurnout } from "../../api/client";
import { useUserStore } from "../../store/useUserStore";
import { HabitCard } from "../../components/HabitCard";
import { triggerHaptic } from "../../utils/animationManager";
import { COLORS } from "../../theme/theme";
import { setupNotifications, cancelHabitReminder, scheduleSmartReminder } from "../../services/notificationService";
import { Brain, Flame, Activity, Zap, Target, ChevronRight, Trophy } from "lucide-react-native";
import { ProgressRing } from "../../components/ProgressRing";
import { LevelHeader } from "../../components/LevelHeader";
import { MotiView } from "moti";

export default function HomeScreen({ navigation }: any) {
  const { token, id, xp, level, coins, streakFreeze, setUserInfo } = useUserStore();
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

  const { data: burnoutStatus } = useQuery({
    queryKey: ['burnout', id],
    queryFn: () => getBurnout(token!),
    enabled: !!id && !!token,
  });

  const { data: aiInsight } = useQuery({
    queryKey: ['aiInsight', id],
    queryFn: () => api('/gamification/ai/insight', 'GET', null, token),
    enabled: !!id && !!token,
  });

  useEffect(() => {
    if (habits && habits.length > 0) {
      checkStreakRisk();
    }
  }, [habits]);

  const checkStreakRisk = async () => {
    // This is a simplified check. In a real app, we'd check if any habit was missed yesterday.
    // For now, we'll offer freeze if they have one and haven't used it for a habit that was missed.
    // The backend handle the actual logic.
  };

  const handleUseFreeze = async (habitId: string) => {
    try {
      const res = await useFreeze(habitId, token!);
      if (res.status === "streak saved") {
        Alert.alert("Streak Saved! ❄️", "Your streak is protected.");
        setUserInfo({ streakFreeze: res.remaining_freezes });
        queryClient.invalidateQueries({ queryKey: ['habits'] });
      } else {
        Alert.alert("Not Needed", "Your streak is already safe or you have no freezes left.");
      }
    } catch (err) {
      console.error("Freeze failed", err);
    }

  };

  const offerFreeze = (habitId: string, habitName: string) => {
    Alert.alert(
      "Streak at Risk",
      `You missed "${habitName}" yesterday. Use a Streak Freeze to save your streak?`,
      [
        { text: "Skip", style: "cancel" },
        { text: "Use Freeze", onPress: () => handleUseFreeze(habitId) }
      ]
    );
  };

  const shareWin = async (streak: number) => {
    try {
        const isAvailable = await Sharing.isAvailableAsync();
        if (isAvailable) {
            await Sharing.shareAsync(`🔥 I'm on a ${streak}-day streak on HabitHero! Joining the consistency revolution.`, {
                dialogTitle: "Share your progress",
            });
            triggerHaptic("coins");
            // Reward for sharing
            setUserInfo({ coins: coins + 20 });
        }
    } catch (err) {
        console.log("Sharing failed", err);
    }
  };

  const completeMutation = useMutation({
    mutationFn: (habitId: string) => api(`/habits/complete`, 'POST', { habit_id: habitId }, token),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['habits'] });
      queryClient.invalidateQueries({ queryKey: ['todayStatus'] });
      
      const oldLevel = level;
      useUserStore.getState().setUserInfo({ 
        xp: data.xp, 
        currentXP: data.current_xp,
        next_level_xp: data.next_level_xp,
        level: data.level,
        coins: data.coins 
      });

      if (data.level > oldLevel) {
        triggerHaptic("level_up");
        Alert.alert("🎉 Level Up!", `Congratulations! You've reached Level ${data.level}. Keep up the amazing consistency!`);
      } else {
        // Successful habit completion - prompt share
        Alert.alert("Nice Work! 🔥", "You completed your habit. Share your win to earn +20 coins?", [
            { text: "No thanks", style: "cancel" },
            { text: "Share Win", onPress: () => shareWin(data.streak) }
        ]);
      }

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
        {/* 🔥 HEADER (Identity & Progress) */}
        <View style={styles.header}>
          <View style={{ flexDirection: 'row', alignItems: 'center', gap: 15 }}>
            <ProgressRing progress={currentXP / nextLevelXP} size={80} strokeWidth={8} />
            <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' }}>
              <LevelHeader 
                level={level || 1} 
                currentXP={xp || 0} 
                nextLevelXP={next_level_xp || 100} 
              />
              <TouchableOpacity 
                onPress={() => navigation.navigate("Badges")}
                style={styles.badgeEntry}
              >
                <Trophy size={20} color={COLORS.primary} />
                <View style={styles.badgeDot} />
              </TouchableOpacity>
            </View>
          </View>
          <View style={styles.headerRight}>
            <Text style={styles.streak}>🔥 {5}</Text>
            <View style={styles.freezeBadge}>
                <Text style={styles.freezeText}>❄️ {streakFreeze || 0}</Text>
            </View>
          </View>
        </View>

        {/* 🤖 AI HABIT COACH */}
        <MotiView 
            from={{ opacity: 0, translateY: 20 }}
            animate={{ opacity: 1, translateY: 0 }}
            style={styles.coachCard}
        >
            <View style={styles.coachIcon}>
                <Brain size={20} color={COLORS.secondary} />
            </View>
            <View style={{ flex: 1 }}>
                <Text style={styles.coachLabel}>AI Habit Coach</Text>
                <Text style={styles.coachMessage}>
                    {aiInsight?.message || "Analyzing your patterns... Check back soon!"}
                </Text>
            </View>
            <TouchableOpacity 
                style={styles.coachAction}
                onPress={() => navigation.navigate("Referral")}
            >
                <Text style={styles.coachActionText}>Gift 50 Coins</Text>
            </TouchableOpacity>
        </MotiView>

        {/* ⚡ DAILY CHALLENGE */}
        <TouchableOpacity style={styles.challengeCard}>
            <View style={{ flexDirection: 'row', alignItems: 'center', gap: 10 }}>
                <View style={styles.zapIcon}>
                    <Zap size={16} color="#000" fill="#000" />
                </View>
                <View style={{ flex: 1 }}>
                    <Text style={styles.challengeTitle}>Daily Boost: Complete 3 Habits</Text>
                    <Text style={styles.challengeReward}>+30 XP Bonus</Text>
                </View>
                <View style={styles.challengeProgress}>
                    <Text style={styles.challengeProgressText}>2/3</Text>
                </View>
            </View>
        </TouchableOpacity>

        {/* 🧘 FOCUS MODE ENTRY */}
        <TouchableOpacity 
          style={styles.focusEntry}
          onPress={() => navigation.navigate("FocusMode")}
        >
          <Target size={20} color="#fff" />
          <Text style={styles.focusEntryText}>Start Deep Work Session</Text>
          <ChevronRight size={18} color="#fff" style={{ marginLeft: 'auto' }} />
        </TouchableOpacity>

        {/* 📊 PROGRESS BOX */}
        <View style={styles.progressBox}>
          <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginBottom: 10 }}>
            <Text style={styles.progressLabel}>Today's Quest</Text>
            <Text style={styles.progressValue}>
                {habits?.filter((h: any) => completedIds.includes(h.id) || optimisticCompleted.includes(h.id)).length || 0}/{habits?.length || 0}
            </Text>
          </View>
          <View style={styles.progressContainer}>
            <Animated.View style={[styles.progressBar, progressStyle]} />
          </View>
        </View>

        {/* 🤖 SMART INSIGHT / BURNOUT */}
        {burnoutStatus?.burnout ? (
          <Animated.View entering={FadeInUp} style={[styles.insightCard, { borderColor: COLORS.error }]}>
            <Activity size={18} color={COLORS.error} />
            <View style={{ flex: 1 }}>
              <Text style={[styles.insightText, { color: COLORS.error }]}>🧘 Let's slow down</Text>
              <Text style={{ color: COLORS.text, fontSize: 12, opacity: 0.8 }}>You've been inconsistent. Let's focus on just 1 habit today.</Text>
            </View>
          </Animated.View>
        ) : recommendations?.insights?.[0] && (
          <Animated.View entering={FadeInUp} style={styles.insightCard}>
            <Brain size={18} color={COLORS.primary} />
            <Text style={styles.insightText}>{recommendations.insights[0]}</Text>
          </Animated.View>
        )}

        {/* 🎯 HABITS */}
        <Text style={styles.section}>Today's Actions</Text>

        <FlatList
          data={habits || []}
          keyExtractor={(item) => item.id}
          showsVerticalScrollIndicator={false}
          refreshControl={
            <RefreshControl refreshing={isLoading} onRefresh={refetch} tintColor={COLORS.primary} />
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

        {/* ⚡ QUICK ACTIONS */}
        <View style={styles.actionsRow}>
            <TouchableOpacity 
              style={styles.addBtn}
              onPress={() => navigation.navigate("AddHabit")}
            >
              <Text style={styles.addText}>+ New Habit</Text>
            </TouchableOpacity>
        </View>

        {/* 💰 FOOTER (Rewards) */}
        <View style={styles.footer}>
          <Text style={styles.coins}>💰 {coins || 0}</Text>
          <TouchableOpacity onPress={() => navigation.navigate("Shop")}>
            <Text style={styles.shop}>🛒 Reward Shop</Text>
          </TouchableOpacity>
        </View>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 25,
    marginTop: 10,
  },
  headerRight: {
    alignItems: 'flex-end',
    gap: 8,
  },
  streak: {
    color: COLORS.accent,
    fontSize: 20,
    fontWeight: '900',
  },
  level: {
    color: COLORS.primary,
    fontSize: 14,
    fontWeight: '600',
    marginTop: 2,
  },
  freezeBadge: {
    backgroundColor: 'rgba(56, 189, 248, 0.1)',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: 'rgba(56, 189, 248, 0.2)',
  },
  freezeText: {
    color: COLORS.primary,
    fontSize: 14,
    fontWeight: '700',
  },
  progressBox: {
    backgroundColor: COLORS.surface,
    padding: 16,
    borderRadius: 20,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: COLORS.glassBorder,
  },
  progressLabel: {
    color: COLORS.text,
    fontSize: 16,
    fontWeight: '700',
  },
  progressValue: {
    color: COLORS.textSecondary,
    fontSize: 14,
    fontWeight: '600',
  },
  progressContainer: {
    height: 8,
    backgroundColor: COLORS.surfaceLight,
    borderRadius: 10,
    overflow: 'hidden',
  },
  progressBar: {
    height: '100%',
    backgroundColor: COLORS.secondary,
  },
  coachCard: {
    backgroundColor: COLORS.surface,
    padding: 15,
    borderRadius: 20,
    marginBottom: 15,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 15,
    borderWidth: 1,
    borderColor: 'rgba(139, 92, 246, 0.1)',
  },
  coachIcon: {
    backgroundColor: 'rgba(139, 92, 246, 0.1)',
    padding: 10,
    borderRadius: 12,
  },
  coachLabel: {
    color: COLORS.text,
    fontSize: 12,
    fontWeight: '800',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  coachMessage: {
    color: COLORS.textDim,
    fontSize: 14,
    fontWeight: '600',
    marginTop: 2,
  },
  coachAction: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 10,
  },
  coachActionText: {
    color: COLORS.primary,
    fontSize: 12,
    fontWeight: '700',
  },
  challengeCard: {
    backgroundColor: COLORS.surface,
    padding: 15,
    borderRadius: 20,
    marginBottom: 15,
    borderWidth: 1,
    borderColor: 'rgba(0, 255, 204, 0.1)',
  },
  zapIcon: {
    backgroundColor: COLORS.primary,
    padding: 8,
    borderRadius: 12,
  },
  challengeTitle: {
    color: COLORS.text,
    fontSize: 14,
    fontWeight: '700',
  },
  challengeReward: {
    color: COLORS.primary,
    fontSize: 12,
    fontWeight: '600',
  },
  challengeProgress: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 10,
  },
  challengeProgressText: {
    color: COLORS.text,
    fontSize: 12,
    fontWeight: '700',
  },
  focusEntry: {
    backgroundColor: '#111',
    flexDirection: 'row',
    alignItems: 'center',
    padding: 15,
    borderRadius: 20,
    marginBottom: 25,
    borderWidth: 1,
    borderColor: '#333',
    gap: 12,
  },
  focusEntryText: {
    color: COLORS.text,
    fontSize: 15,
    fontWeight: '600',
  },
  badgeEntry: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    padding: 10,
    borderRadius: 15,
    marginLeft: 10,
    position: 'relative',
  },
  badgeDot: {
    position: 'absolute',
    top: 8,
    right: 8,
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: COLORS.secondary,
  },
  insightCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.surface,
    padding: 16,
    borderRadius: 20,
    marginBottom: 25,
    gap: 12,
    borderWidth: 1,
    borderColor: COLORS.glassBorder,
  },
  insightText: {
    color: COLORS.primary,
    fontSize: 14,
    fontWeight: '600',
    flex: 1,
  },
  section: {
    color: COLORS.textSecondary,
    fontSize: 14,
    fontWeight: '800',
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginBottom: 15,
  },
  actionsRow: {
    marginTop: 10,
    marginBottom: 10,
  },
  addBtn: {
    backgroundColor: COLORS.secondary,
    padding: 18,
    borderRadius: 20,
    alignItems: 'center',
    shadowColor: COLORS.secondary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 10,
    elevation: 8,
  },
  addText: {
    color: '#000',
    fontSize: 16,
    fontWeight: '800',
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 10,
    paddingTop: 10,
  },
  coins: {
    color: COLORS.gold,
    fontSize: 18,
    fontWeight: '800',
  },
  shop: {
    color: COLORS.primary,
    fontSize: 16,
    fontWeight: '700',
  },
});
