import React, { useState, useEffect } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  ScrollView, 
  RefreshControl, 
  SafeAreaView 
} from 'react-native';
import { COLORS, SPACING, TYPOGRAPHY } from '../theme/theme';
import { api } from '../api/client';
import { useUserStore } from '../store/useUserStore';
import AICoachMessage from '../components/AICoachMessage';
import StreakTension from '../components/StreakTension';
import HabitCompletionAnimation from '../components/HabitCompletionAnimation';
import { GlassCard } from '../components/GlassCard';
import XPProgressRing from '../components/XPProgressRing';
import XPProgressRing from '../components/XPProgressRing';
import { useRewardSystem } from '../hooks/useRewardSystem';
import { soundEngine } from '../services/SoundEngine';
import XPBurst from '../components/XPBurst';
import CoinFly from '../components/CoinFly';
import ConfettiExplosion from '../components/ConfettiExplosion';
import RewardBox from '../components/RewardBox';
import ComboStreak from '../components/ComboStreak';

export default function HomeScreen() {
  const [refreshing, setRefreshing] = useState(false);
  const [userState, setUserState] = useState<any>(null);
  const [habits, setHabits] = useState([
    { id: '1', name: 'Morning Meditation', difficulty: 'easy' },
    { id: '2', name: 'Deep Work Session', difficulty: 'hard' },
    { id: '3', name: 'Daily Reading', difficulty: 'medium' }
  ]);
  
  const {
    activeRewards,
    triggerHabitCompletion,
    removeReward
  } = useRewardSystem();

  useEffect(() => {
    soundEngine.initialize();
    return () => {
      soundEngine.dispose();
    };
  }, []);
  
  const { token, user } = useUserStore();
  const isHindi = false; // Mocked

  const fetchState = async () => {
    try {
      const response = await api("/habit/state", "GET", null, token!);
      setUserState(response);
    } catch (error) {
      console.error('Failed to fetch user state:', error);
    }
  };

  const handleHabitComplete = async (habit: any) => {
    try {
      const result = await api("/habit/complete", "POST", {
        habit_id: habit.id,
        habit_name: habit.name,
        difficulty: habit.difficulty,
        current_streak: userState?.user_state?.current_streak || 7
      }, token!);
      
      if (result.success) {
        // Trigger complex multi-sensory reward sequence
        triggerHabitCompletion(habit, result, { x: 150, y: 400 });
      }
      
      // Refresh state after completion
      fetchState();
      return result;
    } catch (error) {
      console.error('Habit completion failed:', error);
      return { success: false };
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchState();
    setRefreshing(false);
  };

  useEffect(() => {
    if (token) {
      fetchState();
    }
  }, [token]);

  return (
    <SafeAreaView style={styles.safeArea}>
      {/* Animation Overlays */}
      {activeRewards.xpBursts.map((burst) => (
        <XPBurst
          key={burst.id}
          value={burst.value}
          position={{ x: burst.x, y: burst.y }}
        />
      ))}

      {activeRewards.coins.map((coin) => (
        <CoinFly
          key={coin.id}
          id={parseInt(coin.id)}
          startX={coin.startX}
          startY={coin.startY}
          endX={coin.endX}
          endY={coin.endY}
          delay={Math.random() * 200}
        />
      ))}

      {activeRewards.rewardBoxes.map((box) => (
        <RewardBox
          key={box.id}
          reward={box.reward}
          position={{ x: box.x, y: box.y }}
          onReveal={(reward) => {
            triggerHabitCompletion({ difficulty: 'medium' }, { rewards: { total_xp: reward } }, { x: box.x, y: box.y });
            removeReward('rewardBoxes', box.id);
          }}
        />
      ))}

      {activeRewards.combos.map((combo) => (
        <ComboStreak
          key={combo.id}
          count={combo.count}
          position={{ x: combo.x, y: combo.y }}
          onComplete={() => removeReward('combos', combo.id)}
        />
      ))}

      <ConfettiExplosion visible={activeRewards.confetti} intensity={30} />

      <ScrollView 
        style={styles.container}
        contentContainerStyle={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={COLORS.primary} />
        }
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.greeting}>
            {isHindi ? 'नमस्ते,' : 'Hello,'} {user?.email?.split('@')[0]}
          </Text>
          <Text style={styles.title}>
            {isHindi ? 'आज का लक्ष्य' : "Today's Rituals"}
          </Text>
        </View>

        {/* Streak Tension */}
        <StreakTension 
          currentStreak={userState?.user_state?.current_streak || 7}
          lastActivity={new Date().toISOString()}
          isHindi={isHindi}
        />

        {/* AI Coach Message */}
        {userState?.ai_advice && (
          <View style={styles.section}>
            <AICoachMessage 
              currentStreak={userState.user_state.current_streak}
              recentFailures={1}
              isHindi={isHindi}
            />
          </View>
        )}

        {/* Progress Overview Card */}
        <GlassCard style={styles.progressCard}>
          <View style={styles.progressHeader}>
            <XPProgressRing 
              progress={((userState?.user_state?.engagement_score || 0) % 100) / 100}
              size={80}
              strokeWidth={6}
            />
            <View style={styles.progressTextContainer}>
              <Text style={styles.levelText}>LEVEL {userState?.user_state?.level || 3}</Text>
              <Text style={styles.xpText}>{userState?.user_state?.engagement_score?.toFixed(0)} Points Earned</Text>
            </View>
            <View style={styles.badge}>
              <Text style={styles.badgeText}>{userState?.user_state?.mode?.toUpperCase() || 'NORMAL'}</Text>
            </View>
          </View>
        </GlassCard>

        {/* Habits Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>
            {isHindi ? 'आज की आदतें' : "Active Rituals"}
          </Text>
          {habits.map(habit => (
            <HabitCompletionAnimation
              key={habit.id}
              habit={habit}
              onComplete={handleHabitComplete}
              isHindi={isHindi}
            />
          ))}
        </View>

        {/* Mystery Reward Tease */}
        {userState?.gamification?.anticipation_loop && (
          <View style={styles.milestoneBox}>
            <Text style={styles.milestoneText}>
              {userState.gamification.anticipation_loop.message}
            </Text>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: COLORS.background },
  container: { flex: 1 },
  content: { padding: 20, paddingBottom: 40 },
  header: { marginBottom: 24 },
  greeting: { ...TYPOGRAPHY.body, color: COLORS.textSecondary },
  title: { ...TYPOGRAPHY.h1, color: COLORS.text, marginTop: 4 },
  section: { marginTop: 24 },
  sectionTitle: { ...TYPOGRAPHY.h2, color: COLORS.text, marginBottom: 16 },
  progressCard: { padding: 20, marginTop: 24 },
  progressHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  progressTextContainer: { flex: 1, marginLeft: 16 },
  levelText: { ...TYPOGRAPHY.body, fontWeight: '800', color: COLORS.primary },
  xpText: { ...TYPOGRAPHY.caption, color: COLORS.textSecondary },
  badge: { backgroundColor: COLORS.primary, paddingHorizontal: 12, paddingVertical: 4, borderRadius: 12 },
  badgeText: { fontSize: 10, fontWeight: '900', color: '#fff' },
  milestoneBox: { 
    marginTop: 24, 
    backgroundColor: 'rgba(168, 85, 247, 0.1)', 
    padding: 16, 
    borderRadius: 16, 
    borderWidth: 1, 
    borderColor: 'rgba(168, 85, 247, 0.2)' 
  },
  milestoneText: { ...TYPOGRAPHY.body, color: '#a855f7', textAlign: 'center', fontWeight: '600' }
});
