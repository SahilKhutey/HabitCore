import React, { useState, useEffect, useCallback } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  ScrollView, 
  RefreshControl, 
  SafeAreaView,
  Modal,
  TouchableOpacity
} from 'react-native';
import { COLORS, SPACING, TYPOGRAPHY } from '../../src/theme/theme';
import { api } from '../../src/api/client';
import { useUserStore } from '../../src/store/useUserStore';
import HabitCompletionAnimation from '../../src/components/HabitCompletionAnimation';
import { GlassCard } from '../../src/components/GlassCard';
import XPProgressRing from '../../src/components/XPProgressRing';
import { useRewardSystem } from '../../src/hooks/useRewardSystem';
import { soundEngine } from '../../src/services/SoundEngine';
import XPBurst from '../../src/components/XPBurst';
import CoinFly from '../../src/components/CoinFly';
import ConfettiExplosion from '../../src/components/ConfettiExplosion';
import { AddHabitModal } from '../../src/components/AddHabitModal';
import { HabitHeader } from '../../src/components/HabitHeader';
import ArchetypeSelector from '../../src/components/ArchetypeSelector';
import DailyCheckin from '../../src/components/DailyCheckin';
import { Brain, Zap, ChevronRight, Plus, Trophy, Heart } from 'lucide-react-native';
import { MotiView, AnimatePresence } from 'moti';

const QUICK_HABITS = [
  { emoji: '💪', name: 'Morning Workout', difficulty: 'hard', time: '07:00' },
  { emoji: '🧘', name: 'Meditation', difficulty: 'medium', time: '08:00' },
  { emoji: '📚', name: 'Learning Block', difficulty: 'medium', time: '19:00' },
  { emoji: '💧', name: 'Drink 2L Water', difficulty: 'easy', time: '09:00' },
  { emoji: '📓', name: 'Gratitude Journal', difficulty: 'easy', time: '21:00' },
  { emoji: '🚶', name: 'Evening Walk', difficulty: 'easy', time: '18:30' },
];

export default function HomeScreen() {
  const [refreshing, setRefreshing] = useState(false);
  const [isAddModalVisible, setIsAddModalVisible] = useState(false);
  const [userState, setUserState] = useState<any>(null);
  const [habits, setHabits] = useState<any[]>([]);
  const [challenge, setChallenge] = useState<any>(null);
  const [aiInsight, setAiInsight] = useState<string>('');
  const [showArchetype, setShowArchetype] = useState(false);
  const [showCheckin, setShowCheckin] = useState(false);
  const [todayCheckin, setTodayCheckin] = useState<any>(null);
  const { token, currentXP, nextLevelXP, level, coins, setUserInfo } = useUserStore();
  
  const {
    activeRewards,
    triggerHabitCompletion
  } = useRewardSystem();

  useEffect(() => {
    const init = async () => {
      await soundEngine.initialize();
      if (token) {
        fetchState();
        fetchHabits();
        fetchChallenge();
        fetchCheckinStatus();
      }
    };
    init();
    
    return () => {
      soundEngine.dispose();
    };
  }, [token]);

  const fetchCheckinStatus = async () => {
    if (!token) return;
    try {
      const [checkinRes, stateRes] = await Promise.all([
        api('/psychological/today-checkin', 'GET', null, token),
        api('/habits/state', 'GET', null, token),
      ]);
      setTodayCheckin(checkinRes?.done ? checkinRes.checkin : null);
      // Show archetype selector for new users without an archetype
      if (stateRes?.user_state && !stateRes.user_state.archetype) {
        setTimeout(() => setShowArchetype(true), 1500);
      }
    } catch (e) { console.error('Checkin status error:', e); }
  };
  
  const fetchChallenge = async () => {
    try {
      const [challengeRes, recRes] = await Promise.all([
        api('/psychological/daily-challenge', 'GET', null, token!),
        api('/analytics/recommendations', 'GET', null, token!),
      ]);
      setChallenge(challengeRes?.challenge);
      if (recRes?.insights?.length > 0) setAiInsight(recRes.insights[0]);
    } catch (e) {
      console.error('Challenge fetch failed:', e);
    }
  };

  const fetchState = async () => {
    try {
      const response = await api("/habits/state", "GET", null, token!);
      setUserState(response);
      setUserInfo({
        level: response.user_state.level,
        currentXP: response.user_state.xp % 100,
        nextLevelXP: 100,
        coins: response.user_state.coins || 0,
        identityPulse: response.user_state.identity_pulse || 0
      });
    } catch (error) {
      console.error('Failed to fetch user state:', error);
    }
  };

  const fetchHabits = async () => {
    try {
      const response = await api("/habits/", "GET", null, token!);
      const mappedHabits = response.map((h: any) => ({
        ...h,
        duration: h.time || 'Daily',
        xp_reward: h.difficulty === 'hard' ? 150 : (h.difficulty === 'medium' ? 80 : 40)
      }));
      setHabits(mappedHabits);
    } catch (error) {
      console.error('Failed to fetch habits:', error);
    }
  };

  const handleHabitComplete = async (habit: any) => {
    try {
      const result = await api("/habits/complete", "POST", {
        habit_id: habit.id,
        habit_name: habit.name,
        difficulty: habit.difficulty,
        current_streak: userState?.user_state?.current_streak || 1
      }, token!);
      
      if (result.success) {
        triggerHabitCompletion(habit, result, { x: 150, y: 400 });
        fetchState();
      }
      return result;
    } catch (error) {
      console.error('Habit completion failed:', error);
      return { success: false };
    }
  };

  const handleAddHabit = async (habitData: { name: string; time: string; difficulty: string }) => {
    try {
      await api("/habits/create", "POST", habitData, token!);
      await fetchHabits();
    } catch (error) {
      console.error('Failed to create habit:', error);
    }
  };

  const handleSeed = async () => {
    try {
      setRefreshing(true);
      await api("/habits/seed", "POST", {}, token!);
      await Promise.all([fetchState(), fetchHabits()]);
      setRefreshing(false);
    } catch (error) {
      console.error('Seed failed:', error);
      setRefreshing(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await Promise.all([fetchState(), fetchHabits()]);
    setRefreshing(false);
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      {activeRewards.xpBursts.map((burst) => (
        <XPBurst key={burst.id} value={burst.value} position={{ x: burst.x, y: burst.y }} />
      ))}
      {activeRewards.coins.map((coin) => (
        <CoinFly key={coin.id} id={parseInt(coin.id)} startX={coin.startX} startY={coin.startY} endX={coin.endX} endY={coin.endY} />
      ))}
      <ConfettiExplosion visible={activeRewards.confetti} intensity={30} />

      <ScrollView 
        style={styles.container}
        contentContainerStyle={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={COLORS.primary} />
        }
      >
        <View style={styles.headerRow}>
          <View>
            <Text style={styles.greeting}>COMMAND CENTER</Text>
            <Text style={styles.subtitle}>Day {userState?.user_state?.current_streak || 0} Streak</Text>
          </View>
          <TouchableOpacity style={styles.profileBtn}>
            <View style={styles.avatarPlaceholder}>
              <Text style={styles.avatarText}>SK</Text>
            </View>
          </TouchableOpacity>
        </View>

        <HabitHeader
          level={level || 1}
          currentXP={userState?.user_state?.xp || currentXP || 0}
          nextLevelXP={nextLevelXP || 100}
          streak={userState?.user_state?.current_streak || 0}
          coins={coins || userState?.user_state?.coins || 0}
          identityGoal={userState?.user_state?.identity_goal || 'Pioneer'}
        />

        {/* MORNING CHECK-IN BANNER */}
        <AnimatePresence>
          {!todayCheckin && (
            <MotiView from={{ opacity: 0, translateY: -8 }} animate={{ opacity: 1, translateY: 0 }} exit={{ opacity: 0 }} transition={{ type: 'spring' }}>
              <TouchableOpacity onPress={() => setShowCheckin(true)}>
                <GlassCard style={styles.checkinBanner}>
                  <View style={styles.checkinBannerLeft}>
                    <Heart size={18} color="#f472b6" />
                    <View>
                      <Text style={styles.checkinBannerTitle}>Daily Check-In Pending</Text>
                      <Text style={styles.checkinBannerSub}>30 sec · Mood, Energy & Sleep</Text>
                    </View>
                  </View>
                  <View style={styles.checkinBannerBtn}>
                    <Text style={styles.checkinBannerBtnText}>Start →</Text>
                  </View>
                </GlassCard>
              </TouchableOpacity>
            </MotiView>
          )}
        </AnimatePresence>

        {(aiInsight || challenge) && (
          <MotiView
            from={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ type: 'spring', delay: 150 }}
          >
            <GlassCard variant="ai" style={styles.aiCard}>
              <View style={styles.aiHeader}>
                <Brain size={18} color={COLORS.secondary} />
                <Text style={styles.aiTitle}>COGNITIVE INSIGHT</Text>
                <View style={styles.liveDot} />
              </View>
              <Text style={styles.aiMessage}>
                {aiInsight || 'Maintain your morning streak to stabilize your identity alignment.'}
              </Text>
              {challenge && (
                <View style={styles.challengeRow}>
                  <Trophy size={14} color={COLORS.gold} />
                  <Text style={styles.challengeText}>
                    Challenge: {challenge.challenge || 'Complete 3 habits today'}
                  </Text>
                  <View style={styles.xpBadge}>
                    <Text style={styles.xpBadgeText}>+{challenge.xp_reward || 50} XP</Text>
                  </View>
                </View>
              )}
            </GlassCard>
          </MotiView>
        )}

        <View style={styles.questHeader}>
          <Text style={styles.sectionTitle}>TODAY'S HABITS</Text>
          <TouchableOpacity onPress={() => setIsAddModalVisible(true)}>
            <Text style={styles.viewAll}>+ Add Ritual</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.habitList}>
          {habits.length > 0 ? (
            habits.map(habit => (
              <HabitCompletionAnimation
                key={habit.id}
                habit={habit}
                onComplete={handleHabitComplete}
              />
            ))
          ) : (
            <GlassCard style={styles.emptyCard}>
              <Text style={styles.emptyText}>No rituals activated.</Text>
              <Text style={styles.emptyHint}>Quick add a habit to begin:</Text>
              <View style={styles.quickGrid}>
                {QUICK_HABITS.map((qh, i) => (
                  <TouchableOpacity key={i} style={styles.quickChip} onPress={() => handleAddHabit({ name: qh.name, time: qh.time, difficulty: qh.difficulty })}>
                    <Text style={styles.quickEmoji}>{qh.emoji}</Text>
                    <Text style={styles.quickName}>{qh.name}</Text>
                  </TouchableOpacity>
                ))}
              </View>
              <TouchableOpacity style={styles.seedBtn} onPress={handleSeed}>
                <Text style={styles.seedBtnText}>Or seed all starter habits →</Text>
              </TouchableOpacity>
            </GlassCard>
          )}
        </View>

        <TouchableOpacity style={styles.challengeCard}>
          <View style={styles.challengeIcon}>
            <Zap size={20} color="#000" fill="#000" />
          </View>
          <View style={{ flex: 1 }}>
            <Text style={styles.challengeTitle}>
              Daily Goal: {userState?.habits_completed_today?.length ?? 0}/{userState?.user_state?.daily_habit_goal ?? 3} Habits
            </Text>
            <View style={styles.progressBarBg}>
              <View style={[styles.progressBarFill, { 
                width: `${Math.min(100, ((userState?.habits_completed_today?.length ?? 0) / (userState?.user_state?.daily_habit_goal ?? 3)) * 100)}%` 
              }]} />
            </View>
          </View>
          <Text style={styles.challengeReward}>+{challenge?.xp_reward ?? 30} XP</Text>
        </TouchableOpacity>
      </ScrollView>

      <TouchableOpacity 
        style={styles.fab} 
        onPress={() => setIsAddModalVisible(true)}
      >
        <Plus color="#000" size={24} />
      </TouchableOpacity>

      {/* ARCHETYPE SELECTOR (first run) */}
      <Modal visible={showArchetype} animationType="slide" presentationStyle="fullScreen">
        <ArchetypeSelector onComplete={(arch) => { setShowArchetype(false); fetchHabits(); fetchState(); }} />
      </Modal>

      {/* DAILY CHECK-IN */}
      <Modal visible={showCheckin} animationType="slide" presentationStyle="pageSheet" onRequestClose={() => setShowCheckin(false)}>
        <View style={styles.modal}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>Daily Check-In</Text>
            <TouchableOpacity onPress={() => setShowCheckin(false)}><Text style={styles.modalClose}>✕</Text></TouchableOpacity>
          </View>
          <DailyCheckin onComplete={(res) => { setShowCheckin(false); setTodayCheckin(res?.checkin || {}); }} />
        </View>
      </Modal>

      <AddHabitModal
        visible={isAddModalVisible}
        onClose={() => setIsAddModalVisible(false)}
        onAdd={handleAddHabit}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: COLORS.background },
  container: { flex: 1 },
  content: { padding: SPACING.margin, paddingBottom: 100 },
  header: { 
    flexDirection: 'row', 
    justifyContent: 'space-between', 
    alignItems: 'center',
    marginBottom: SPACING.lg
  },
  headerRow: { 
    flexDirection: 'row', 
    justifyContent: 'space-between', 
    alignItems: 'center',
    marginBottom: 12,
  },
  greeting: { ...TYPOGRAPHY.label, color: COLORS.primary },
  subtitle: { ...TYPOGRAPHY.caption, color: COLORS.textDim, marginTop: 2 },
  title: { ...TYPOGRAPHY.h1, marginTop: 2, color: COLORS.text },
  profileBtn: {
    width: 44,
    height: 44,
    borderRadius: 22,
    borderWidth: 1.5,
    borderColor: COLORS.primary,
    padding: 2,
  },
  avatarPlaceholder: {
    flex: 1,
    borderRadius: 20,
    backgroundColor: COLORS.surfaceLight,
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatarText: {
    color: COLORS.primary,
    fontWeight: '700',
    fontSize: 12,
  },
  identityCard: {
    marginBottom: SPACING.lg,
    padding: SPACING.lg,
  },
  identityContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  identityTextContainer: {
    marginLeft: SPACING.lg,
    flex: 1,
  },
  lvlLabel: {
    ...TYPOGRAPHY.h2,
    color: COLORS.text,
  },
  xpLabel: {
    ...TYPOGRAPHY.caption,
    color: COLORS.textSecondary,
    marginTop: 2,
  },
  identityBadge: {
    backgroundColor: 'rgba(0, 255, 204, 0.1)',
    alignSelf: 'flex-start',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
    marginTop: 8,
    borderWidth: 0.5,
    borderColor: 'rgba(0, 255, 204, 0.2)',
  },
  identityBadgeText: {
    fontSize: 9,
    fontFamily: 'SpaceGrotesk_700Bold',
    color: COLORS.primary,
  },
  coinBadge: {
    backgroundColor: 'rgba(255, 215, 0, 0.1)',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 12,
    position: 'absolute',
    top: -10,
    right: -10,
  },
  coinText: {
    fontSize: 12,
    fontWeight: '700',
    color: COLORS.gold,
  },
  aiCard: {
    marginBottom: SPACING.lg,
  },
  aiHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  aiTitle: {
    ...TYPOGRAPHY.label,
    color: COLORS.secondary,
    marginLeft: 8,
    flex: 1,
  },
  liveDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: '#ff4444',
  },
  aiMessage: {
    ...TYPOGRAPHY.body,
    fontSize: 14,
    lineHeight: 20,
    color: COLORS.text,
    opacity: 0.9,
    marginBottom: 4,
  },
  aiAction: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 12,
  },
  aiActionText: {
    ...TYPOGRAPHY.label,
    fontSize: 12,
    color: COLORS.secondary,
    marginRight: 4,
  },
  challengeRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 10,
    paddingTop: 10,
    borderTopWidth: 1,
    borderTopColor: 'rgba(255,255,255,0.05)',
    gap: 6,
  },
  challengeText: {
    ...TYPOGRAPHY.caption,
    color: COLORS.text,
    flex: 1,
    fontSize: 12,
  },
  xpBadge: {
    backgroundColor: 'rgba(251,191,36,0.15)',
    borderRadius: 8,
    paddingHorizontal: 8,
    paddingVertical: 3,
  },
  xpBadgeText: {
    fontFamily: 'SpaceGrotesk_700Bold',
    fontSize: 10,
    color: COLORS.gold,
  },
  questHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: SPACING.md,
  },
  sectionTitle: {
    ...TYPOGRAPHY.label,
    color: COLORS.textSecondary,
    letterSpacing: 2,
  },
  viewAll: {
    ...TYPOGRAPHY.caption,
    color: COLORS.primary,
  },
  habitList: {
    marginBottom: SPACING.lg,
  },
  challengeCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.03)',
    padding: SPACING.md,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.05)',
  },
  challengeIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: COLORS.primary,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: SPACING.md,
  },
  challengeTitle: {
    ...TYPOGRAPHY.label,
    color: COLORS.text,
    fontSize: 13,
  },
  progressBarBg: {
    height: 4,
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    borderRadius: 2,
    marginTop: 8,
    width: '100%',
  },
  progressBarFill: {
    height: '100%',
    backgroundColor: COLORS.primary,
    borderRadius: 2,
  },
  challengeReward: {
    ...TYPOGRAPHY.label,
    color: COLORS.primary,
    marginLeft: SPACING.md,
  },
  emptyCard: {
    padding: SPACING.xl,
    alignItems: 'center',
    justifyContent: 'center',
    borderStyle: 'dashed',
    borderWidth: 1.5,
    borderColor: 'rgba(255, 255, 255, 0.1)',
  },
  emptyText: {
    ...TYPOGRAPHY.body,
    color: COLORS.textDim,
    textAlign: 'center',
    fontSize: 14,
  },
  seedBtn: {
    backgroundColor: 'rgba(0, 255, 204, 0.1)',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 12,
    marginTop: 16,
    borderWidth: 1,
    borderColor: COLORS.primary,
  },
  seedBtnText: {
    ...TYPOGRAPHY.label,
    color: COLORS.primary,
    fontSize: 12,
  },
  fab: {
    position: 'absolute',
    bottom: 30,
    right: 30,
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: COLORS.primary,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: COLORS.primary,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.4,
    shadowRadius: 12,
    elevation: 8,
    elevation: 8,
  },
  checkinBanner: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    padding: 14, marginBottom: SPACING.md,
    borderColor: 'rgba(244,114,182,0.3)', borderWidth: 1,
  },
  checkinBannerLeft: { flexDirection: 'row', alignItems: 'center', gap: 12, flex: 1 },
  checkinBannerTitle: { fontFamily: 'SpaceGrotesk_600SemiBold', fontSize: 13, color: COLORS.text },
  checkinBannerSub: { fontFamily: 'SpaceGrotesk_500Medium', fontSize: 10, color: COLORS.textSecondary, marginTop: 1 },
  checkinBannerBtn: {
    backgroundColor: 'rgba(244,114,182,0.15)', borderRadius: 10,
    paddingHorizontal: 12, paddingVertical: 7,
    borderWidth: 1, borderColor: 'rgba(244,114,182,0.3)',
  },
  checkinBannerBtnText: { fontFamily: 'SpaceGrotesk_700Bold', fontSize: 12, color: '#f472b6' },
  emptyHint: { fontFamily: 'SpaceGrotesk_500Medium', fontSize: 12, color: COLORS.textDim, marginTop: 8, marginBottom: 16 },
  quickGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginBottom: 16 },
  quickChip: {
    flexDirection: 'row', alignItems: 'center', gap: 6,
    backgroundColor: 'rgba(51,255,214,0.07)', borderRadius: 20,
    paddingHorizontal: 12, paddingVertical: 8,
    borderWidth: 1, borderColor: 'rgba(51,255,214,0.2)',
  },
  quickEmoji: { fontSize: 16 },
  quickName: { fontFamily: 'SpaceGrotesk_500Medium', fontSize: 11, color: COLORS.text },
  modal: { flex: 1, backgroundColor: COLORS.background },
  modalHeader: {
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
    paddingHorizontal: 24, paddingTop: 20, paddingBottom: 16,
    borderBottomWidth: 1, borderBottomColor: 'rgba(255,255,255,0.07)',
  },
  modalTitle: { fontFamily: 'SpaceGrotesk_600SemiBold', fontSize: 20, color: COLORS.text },
  modalClose: { fontFamily: 'SpaceGrotesk_500Medium', fontSize: 14, color: COLORS.textDim },
});
